"""Admin Dashboard Views for Cache Management, Pincode Scaling, and Edit History
"""

import json
import difflib
from datetime import datetime, timedelta
from typing import Dict, List, Any

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import caches, cache
from django.db.models import Count, Avg, Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import User, Booking, Service, AuditLog, NotificationLog, PincodeAnalytics, BusinessAlert
from .permissions import IsSuperAdmin, IsAdminUser
from .notification_service import NotificationService
from . import tasks


class CacheManagementView(View):
    """
    Cache Management Interface for Admins
    Provides cache statistics, selective clearing, and monitoring
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """Get cache statistics and health information"""
        # Allow ops_manager, super_admin, and admin roles
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if request.user.role not in ['super_admin', 'ops_manager', 'admin']:
            return JsonResponse({
                'error': 'Unauthorized',
                'message': f'Your role ({request.user.role}) does not have permission to access cache management. Required roles: super_admin, ops_manager, admin'
            }, status=403)
        
        cache_stats = self._get_cache_statistics()
        return JsonResponse({
            'status': 'success',
            'cache_stats': cache_stats,
            'timestamp': timezone.now().isoformat()
        })
    
    def post(self, request):
        """Clear specific cache categories"""
        # Allow ops_manager, super_admin, and admin roles
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if request.user.role not in ['super_admin', 'ops_manager', 'admin']:
            return JsonResponse({
                'error': 'Unauthorized',
                'message': f'Your role ({request.user.role}) does not have permission to clear cache. Required roles: super_admin, ops_manager, admin'
            }, status=403)
        
        try:
            data = json.loads(request.body)
            cache_type = data.get('cache_type', 'all')
            
            result = self._clear_cache(cache_type)
            
            # Log the cache clear action
            from .utils import AuditLogger
            AuditLogger.log_action(
                user=request.user,
                action='cache_clear',
                resource_type='Cache',
                resource_id=cache_type,
                request=request,
                new_values={'cache_type': cache_type, 'result': result}
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Cache "{cache_type}" cleared successfully',
                'result': result
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to clear cache: {str(e)}'
            }, status=500)
    
    def _get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {}
        
        cache_configs = ['default', 'sessions', 'search_results', 'api_data']
        
        for cache_name in cache_configs:
            try:
                cache_instance = caches[cache_name]
                cache_stats = {
                    'name': cache_name,
                    'backend': str(cache_instance.__class__.__name__),
                    'timeout': getattr(cache_instance, 'default_timeout', 'N/A'),
                    'key_prefix': getattr(cache_instance, 'key_prefix', 'N/A'),
                    'type': 'In-Memory (LocMem)',
                    'status': 'active'
                }
                
                stats[cache_name] = cache_stats
                
            except Exception as e:
                stats[cache_name] = {'error': str(e)}
        
        # Overall health status
        stats['overall_health'] = self._calculate_overall_health(stats)
        
        return stats
    
    def _calculate_overall_health(self, stats: Dict) -> Dict[str, Any]:
        """Calculate overall cache health metrics"""
        healthy_caches = 0
        total_caches = 0
        
        for cache_name, cache_data in stats.items():
            if cache_name == 'overall_health':
                continue
                
            total_caches += 1
            
            if 'error' not in cache_data:
                healthy_caches += 1
        
        health_percentage = (healthy_caches / total_caches * 100) if total_caches > 0 else 0
        
        return {
            'healthy_caches': healthy_caches,
            'total_caches': total_caches,
            'health_percentage': round(health_percentage, 2),
            'cache_type': 'In-Memory (LocMem)',
            'status': 'healthy' if health_percentage >= 80 else 'warning' if health_percentage >= 60 else 'critical'
        }
    
    def _clear_cache(self, cache_type: str) -> Dict[str, Any]:
        """Clear specified cache type"""
        result = {'cleared': [], 'errors': []}
        
        if cache_type == 'all':
            cache_types = ['default', 'sessions', 'search_results', 'api_data']
        else:
            cache_types = [cache_type]
        
        for ct in cache_types:
            try:
                cache_instance = caches[ct]
                cache_instance.clear()
                result['cleared'].append(ct)
            except Exception as e:
                result['errors'].append(f'{ct}: {str(e)}')
        
        return result


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def pincode_scaling_data(request):
    """
    Pincode Scaling Map Visualization Data
    Provides aggregated data for demand, service density, and vendor availability by pincode
    """
    
    # Get query parameters for filtering
    service_type = request.GET.get('service_type')
    days_back = int(request.GET.get('days_back', 30))
    
    # Calculate date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Base booking queryset
    booking_qs = Booking.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    )
    
    # Filter by service type if specified
    if service_type:
        booking_qs = booking_qs.filter(service__category=service_type)
    
    # Aggregate booking data by pincode
    pincode_data = booking_qs.values('pincode').annotate(
        total_bookings=Count('id'),
        completed_bookings=Count('id', filter=Q(status='completed')),
        pending_bookings=Count('id', filter=Q(status='pending')),
        cancelled_bookings=Count('id', filter=Q(status='cancelled')),
        avg_completion_time=Avg('completion_date') # This might need custom calculation
    ).order_by('-total_bookings')
    
    # Get vendor data by pincode
    vendor_data = User.objects.filter(
        role='vendor',
        is_available=True
    ).values('pincode').annotate(
        available_vendors=Count('id')
    )
    
    # Create vendor lookup dict
    vendor_lookup = {item['pincode']: item['available_vendors'] for item in vendor_data}
    
    # Combine data and calculate metrics
    map_data = []
    for item in pincode_data:
        pincode = item['pincode']
        total_bookings = item['total_bookings']
        completed = item['completed_bookings']
        pending = item['pending_bookings']
        cancelled = item['cancelled_bookings']
        
        # Calculate metrics
        completion_rate = (completed / total_bookings * 100) if total_bookings > 0 else 0
        cancellation_rate = (cancelled / total_bookings * 100) if total_bookings > 0 else 0
        available_vendors = vendor_lookup.get(pincode, 0)
        
        # Calculate demand intensity (bookings per vendor)
        demand_intensity = total_bookings / available_vendors if available_vendors > 0 else total_bookings
        
        # Calculate wait time estimate (simplified)
        avg_wait_time = max(1, pending / available_vendors) if available_vendors > 0 else pending
        
        # Determine zone status
        if demand_intensity > 10 and available_vendors < 3:
            zone_status = 'high_demand_low_supply'
        elif demand_intensity < 2 and available_vendors > 5:
            zone_status = 'low_demand_high_supply'
        elif completion_rate > 80 and cancellation_rate < 10:
            zone_status = 'optimal'
        else:
            zone_status = 'balanced'
        
        map_data.append({
            'pincode': pincode,
            'total_bookings': total_bookings,
            'completed_bookings': completed,
            'pending_bookings': pending,
            'cancelled_bookings': cancelled,
            'completion_rate': round(completion_rate, 2),
            'cancellation_rate': round(cancellation_rate, 2),
            'available_vendors': available_vendors,
            'demand_intensity': round(demand_intensity, 2),
            'estimated_wait_time_hours': round(avg_wait_time, 1),
            'zone_status': zone_status,
            # Color intensity for heat map (0-100)
            'heat_intensity': min(100, demand_intensity * 10)
        })
    
    # Get service categories for filtering
    service_categories = list(
        Service.objects.values_list('category', flat=True).distinct()
    )
    
    # Summary statistics
    summary = {
        'total_pincodes': len(map_data),
        'total_bookings': sum(item['total_bookings'] for item in map_data),
        'total_vendors': sum(vendor_lookup.values()),
        'high_demand_zones': len([item for item in map_data if item['zone_status'] == 'high_demand_low_supply']),
        'optimal_zones': len([item for item in map_data if item['zone_status'] == 'optimal']),
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'days': days_back
        },
        'service_categories': service_categories
    }
    
    return Response({
        'status': 'success',
        'data': map_data,
        'summary': summary,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def edit_history_diff_viewer(request):
    """
    Global Edit History Diff Viewer
    Provides audit log data with diff visualization capabilities
    """
    
    # Get query parameters
    model_filter = request.GET.get('model')
    user_filter = request.GET.get('user')
    action_filter = request.GET.get('action')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Build queryset
    queryset = AuditLog.objects.all()
    
    if model_filter:
        queryset = queryset.filter(resource_type__icontains=model_filter)
    
    if user_filter:
        queryset = queryset.filter(user__username__icontains=user_filter)
    
    if action_filter:
        queryset = queryset.filter(action=action_filter)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__gte=start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__lte=end_dt)
        except ValueError:
            pass
    
    # Pagination
    total_count = queryset.count()
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    audit_logs = queryset[start_idx:end_idx]
    
    # Process audit logs and generate diffs
    processed_logs = []
    for log in audit_logs:
        log_data = {
            'id': log.id,
            'user': log.user.username,
            'user_role': log.user.role,
            'action': log.action,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'timestamp': log.timestamp.isoformat(),
            'ip_address': log.ip_address,
            'user_agent': log.user_agent[:100] if log.user_agent else None,  # Truncate for readability
            'old_values': log.old_values,
            'new_values': log.new_values,
            'diff': None
        }
        
        # Generate diff if both old and new values exist
        if log.old_values and log.new_values and log.action == 'update':
            log_data['diff'] = _generate_diff(log.old_values, log.new_values)
        
        processed_logs.append(log_data)
    
    # Get filter options
    filter_options = {
        'models': list(AuditLog.objects.values_list('resource_type', flat=True).distinct()),
        'actions': [choice[0] for choice in AuditLog.ACTION_CHOICES],
        'users': list(User.objects.filter(
            id__in=AuditLog.objects.values_list('user_id', flat=True).distinct()
        ).values_list('username', flat=True))
    }
    
    # Pagination info
    pagination = {
        'page': page,
        'page_size': page_size,
        'total_count': total_count,
        'total_pages': (total_count + page_size - 1) // page_size,
        'has_next': end_idx < total_count,
        'has_previous': page > 1
    }
    
    return Response({
        'status': 'success',
        'data': processed_logs,
        'pagination': pagination,
        'filter_options': filter_options,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def export_edit_history(request):
    """
    Export edit history as CSV or PDF
    """
    
    export_format = request.data.get('format', 'csv')
    filters = request.data.get('filters', {})
    
    # Build queryset with filters (similar to above)
    queryset = AuditLog.objects.all()
    
    # Apply filters
    if filters.get('model'):
        queryset = queryset.filter(resource_type__icontains=filters['model'])
    if filters.get('user'):
        queryset = queryset.filter(user__username__icontains=filters['user'])
    if filters.get('action'):
        queryset = queryset.filter(action=filters['action'])
    if filters.get('start_date'):
        try:
            start_dt = datetime.fromisoformat(filters['start_date'].replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__gte=start_dt)
        except ValueError:
            pass
    if filters.get('end_date'):
        try:
            end_dt = datetime.fromisoformat(filters['end_date'].replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__lte=end_dt)
        except ValueError:
            pass
    
    # Limit to prevent huge exports
    queryset = queryset[:1000]
    
    if export_format == 'csv':
        response_data = _export_to_csv(queryset)
    else:
        response_data = _export_to_pdf(queryset)
    
    return Response({
        'status': 'success',
        'message': f'Export completed in {export_format.upper()} format',
        'record_count': queryset.count(),
        'download_data': response_data,
        'timestamp': timezone.now().isoformat()
    })


def _generate_diff(old_values: dict, new_values: dict) -> List[Dict[str, Any]]:
    """
    Generate human-readable diff between old and new values using difflib
    """
    diffs = []
    
    # Get all keys from both dictionaries
    all_keys = set(old_values.keys()) | set(new_values.keys())
    
    for key in sorted(all_keys):
        old_val = old_values.get(key, '<NOT_SET>')
        new_val = new_values.get(key, '<NOT_SET>')
        
        if old_val != new_val:
            # Convert to strings for diff
            old_str = str(old_val) if old_val is not None else '<NULL>'
            new_str = str(new_val) if new_val is not None else '<NULL>'
            
            # Generate unified diff
            diff_lines = list(difflib.unified_diff(
                old_str.splitlines(keepends=True),
                new_str.splitlines(keepends=True),
                fromfile=f'{key} (old)',
                tofile=f'{key} (new)',
                lineterm=''
            ))
            
            diffs.append({
                'field': key,
                'old_value': old_val,
                'new_value': new_val,
                'diff_lines': diff_lines[2:] if len(diff_lines) > 2 else [],  # Skip header lines
                'change_type': _get_change_type(old_val, new_val)
            })
    
    return diffs


def _get_change_type(old_val, new_val) -> str:
    """Determine the type of change made"""
    if old_val is None or old_val == '<NOT_SET>':
        return 'added'
    elif new_val is None or new_val == '<NOT_SET>':
        return 'removed'
    else:
        return 'modified'


def _export_to_csv(queryset) -> str:
    """Export audit logs to CSV format"""
    import csv
    import io
    import base64
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Timestamp', 'User', 'User Role', 'Action', 'Resource Type', 
        'Resource ID', 'Old Values', 'New Values', 'IP Address'
    ])
    
    # Write data
    for log in queryset:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.username,
            log.user.role,
            log.get_action_display(),
            log.resource_type,
            log.resource_id,
            json.dumps(log.old_values) if log.old_values else '',
            json.dumps(log.new_values) if log.new_values else '',
            log.ip_address or ''
        ])
    
    # Encode as base64 for safe transport
    csv_content = output.getvalue()
    output.close()
    
    return base64.b64encode(csv_content.encode('utf-8')).decode('utf-8')


def _export_to_pdf(queryset) -> str:
    """Export audit logs to PDF format (simplified version)"""
    # This is a simplified implementation
    # In production, you'd want to use a proper PDF library like reportlab
    
    import base64
    
    # Create a simple text-based PDF content
    content = "HOMESERVE PRO - AUDIT LOG REPORT\n"
    content += "=" * 50 + "\n\n"
    content += f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"Total Records: {queryset.count()}\n\n"
    
    for log in queryset:
        content += f"Timestamp: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"User: {log.user.username} ({log.user.role})\n"
        content += f"Action: {log.get_action_display()}\n"
        content += f"Resource: {log.resource_type} #{log.resource_id}\n"
        if log.old_values:
            content += f"Old Values: {json.dumps(log.old_values, indent=2)}\n"
        if log.new_values:
            content += f"New Values: {json.dumps(log.new_values, indent=2)}\n"
        content += "-" * 30 + "\n\n"
    
    # Encode as base64
    return base64.b64encode(content.encode('utf-8')).decode('utf-8')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_dashboard_stats(request):
    """
    Combined dashboard statistics for admin overview
    """
    
    # Cache stats
    cache_view = CacheManagementView()
    cache_stats = cache_view._get_cache_statistics()
    
    # Recent activity stats
    recent_logs = AuditLog.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    )
    
    activity_stats = {
        'total_actions_24h': recent_logs.count(),
        'unique_users_24h': recent_logs.values('user').distinct().count(),
        'top_actions': list(recent_logs.values('action').annotate(
            count=Count('action')
        ).order_by('-count')[:5])
    }
    
    # Pincode performance summary
    total_bookings = Booking.objects.count()
    total_pincodes = Booking.objects.values('pincode').distinct().count()
    
    pincode_stats = {
        'total_pincodes_served': total_pincodes,
        'avg_bookings_per_pincode': round(total_bookings / total_pincodes, 2) if total_pincodes > 0 else 0,
        'active_vendors': User.objects.filter(role='vendor', is_available=True).count()
    }
    
    return Response({
        'status': 'success',
        'cache_health': cache_stats.get('overall_health', {}),
        'activity_stats': activity_stats,
        'pincode_stats': pincode_stats,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def notification_management(request):
    """Manage notifications and automated messaging"""
    
    if request.method == 'GET':
        # Get notification statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Notification stats
        notification_stats = {
            'total_sent_today': NotificationLog.objects.filter(sent_at__date=today).count(),
            'total_sent_week': NotificationLog.objects.filter(sent_at__date__gte=week_ago).count(),
            'success_rate_today': 0,
            'by_type_today': {},
            'by_method_today': {},
            'failed_today': NotificationLog.objects.filter(
                sent_at__date=today, 
                status='failed'
            ).count()
        }
        
        # Calculate success rate
        total_today = notification_stats['total_sent_today']
        if total_today > 0:
            successful_today = NotificationLog.objects.filter(
                sent_at__date=today, 
                status='sent'
            ).count()
            notification_stats['success_rate_today'] = round((successful_today / total_today) * 100, 2)
        
        # Notifications by type today
        type_stats = NotificationLog.objects.filter(
            sent_at__date=today
        ).values('notification_type').annotate(count=Count('id'))
        
        for stat in type_stats:
            notification_stats['by_type_today'][stat['notification_type']] = stat['count']
        
        # Notifications by method today
        method_stats = NotificationLog.objects.filter(
            sent_at__date=today
        ).values('method').annotate(count=Count('id'))
        
        for stat in method_stats:
            notification_stats['by_method_today'][stat['method']] = stat['count']
        
        # Business alerts
        active_alerts = BusinessAlert.objects.filter(status='active').count()
        critical_alerts = BusinessAlert.objects.filter(
            status='active', 
            severity='critical'
        ).count()
        
        # Pincode analytics
        pincode_analytics = {
            'total_pincodes_analyzed': PincodeAnalytics.objects.filter(date=today).count(),
            'high_demand_areas': PincodeAnalytics.objects.filter(
                date=today,
                total_bookings__gt=5
            ).count(),
            'low_vendor_areas': PincodeAnalytics.objects.filter(
                date=today,
                available_vendors__lt=2
            ).count()
        }
        
        return Response({
            'status': 'success',
            'notification_stats': notification_stats,
            'business_alerts': {
                'active_alerts': active_alerts,
                'critical_alerts': critical_alerts
            },
            'pincode_analytics': pincode_analytics,
            'timestamp': timezone.now().isoformat()
        })
    
    elif request.method == 'POST':
        # Trigger manual tasks
        action = request.data.get('action')
        
        try:
            if action == 'generate_analytics':
                task = tasks.generate_pincode_analytics.delay()
                message = f"Analytics generation started. Task ID: {task.id}"
                
            elif action == 'send_demand_alerts':
                task = tasks.send_pincode_demand_alerts.delay()
                message = f"Demand alerts task started. Task ID: {task.id}"
                
            elif action == 'send_bonus_alerts':
                task = tasks.send_vendor_bonus_alerts.delay()
                message = f"Bonus alerts task started. Task ID: {task.id}"
                
            elif action == 'send_promotions':
                task = tasks.send_promotional_campaigns.delay()
                message = f"Promotional campaigns task started. Task ID: {task.id}"
                
            elif action == 'check_signatures':
                task = tasks.check_pending_signatures.delay()
                message = f"Signature check task started. Task ID: {task.id}"
                
            elif action == 'check_payments':
                task = tasks.check_payment_holds.delay()
                message = f"Payment check task started. Task ID: {task.id}"
                
            elif action == 'check_timeouts':
                task = tasks.check_booking_timeouts.delay()
                message = f"Timeout check task started. Task ID: {task.id}"
                
            elif action == 'send_reminders':
                task = tasks.send_vendor_completion_reminders.delay()
                message = f"Completion reminders task started. Task ID: {task.id}"
                
            elif action == 'test_system':
                task = tasks.test_notification_system.delay()
                message = f"Notification system test started. Task ID: {task.id}"
                
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid action specified'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Log the manual trigger
            from .utils import AuditLogger
            AuditLogger.log_action(
                user=request.user,
                action='manual_task_trigger',
                resource_type='CeleryTask',
                resource_id=action,
                request=request,
                new_values={'action': action, 'task_id': task.id}
            )
            
            return Response({
                'status': 'success',
                'message': message,
                'task_id': task.id
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to trigger task: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def notification_logs(request):
    """Get notification logs with filtering"""
    
    # Get query parameters
    page = int(request.GET.get('page', 1))
    per_page = min(int(request.GET.get('per_page', 20)), 100)
    notification_type = request.GET.get('type')
    method = request.GET.get('method')
    status_filter = request.GET.get('status')
    recipient_id = request.GET.get('recipient_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Build query
    queryset = NotificationLog.objects.select_related('recipient').order_by('-sent_at')
    
    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)
    if method:
        queryset = queryset.filter(method=method)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if recipient_id:
        queryset = queryset.filter(recipient_id=recipient_id)
    if date_from:
        queryset = queryset.filter(sent_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(sent_at__date__lte=date_to)
    
    # Paginate
    total_count = queryset.count()
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    notifications = queryset[start_index:end_index]
    
    # Serialize data
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': str(notification.id),
            'recipient': {
                'id': notification.recipient.id,
                'username': notification.recipient.username,
                'email': notification.recipient.email,
                'role': notification.recipient.role
            },
            'notification_type': notification.notification_type,
            'method': notification.method,
            'status': notification.status,
            'subject': notification.subject,
            'message': notification.message[:200] + '...' if len(notification.message) > 200 else notification.message,
            'metadata': notification.metadata,
            'sent_at': notification.sent_at.isoformat(),
            'delivered_at': notification.delivered_at.isoformat() if notification.delivered_at else None,
            'error_message': notification.error_message
        })
    
    return Response({
        'status': 'success',
        'notifications': notification_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'total_pages': (total_count + per_page - 1) // per_page
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def business_alerts(request):
    """Get business alerts with filtering"""
    
    # Get query parameters
    page = int(request.GET.get('page', 1))
    per_page = min(int(request.GET.get('per_page', 20)), 100)
    alert_type = request.GET.get('type')
    severity = request.GET.get('severity')
    status_filter = request.GET.get('status', 'active')
    
    # Build query
    queryset = BusinessAlert.objects.select_related(
        'assigned_to', 'resolved_by', 'related_booking'
    ).order_by('-created_at')
    
    if alert_type:
        queryset = queryset.filter(alert_type=alert_type)
    if severity:
        queryset = queryset.filter(severity=severity)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # Paginate
    total_count = queryset.count()
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    alerts = queryset[start_index:end_index]
    
    # Serialize data
    alert_data = []
    for alert in alerts:
        alert_data.append({
            'id': str(alert.id),
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'status': alert.status,
            'title': alert.title,
            'description': alert.description,
            'metadata': alert.metadata,
            'assigned_to': {
                'id': alert.assigned_to.id,
                'username': alert.assigned_to.username
            } if alert.assigned_to else None,
            'resolved_by': {
                'id': alert.resolved_by.id,
                'username': alert.resolved_by.username
            } if alert.resolved_by else None,
            'created_at': alert.created_at.isoformat(),
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
            'resolution_notes': alert.resolution_notes
        })
    
    return Response({
        'status': 'success',
        'alerts': alert_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'total_pages': (total_count + per_page - 1) // per_page
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def pincode_analytics_view(request):
    """Get pincode analytics data"""
    
    # Get query parameters
    page = int(request.GET.get('page', 1))
    per_page = min(int(request.GET.get('per_page', 20)), 100)
    pincode = request.GET.get('pincode')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Default to last 7 days if no date range specified
    if not date_from:
        date_from = (timezone.now().date() - timedelta(days=7)).isoformat()
    if not date_to:
        date_to = timezone.now().date().isoformat()
    
    # Build query
    queryset = PincodeAnalytics.objects.order_by('-date', 'pincode')
    
    if pincode:
        queryset = queryset.filter(pincode=pincode)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    
    # Paginate
    total_count = queryset.count()
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    analytics = queryset[start_index:end_index]
    
    # Serialize data
    analytics_data = []
    for analytic in analytics:
        analytics_data.append({
            'pincode': analytic.pincode,
            'date': analytic.date.isoformat(),
            'total_bookings': analytic.total_bookings,
            'pending_bookings': analytic.pending_bookings,
            'completed_bookings': analytic.completed_bookings,
            'cancelled_bookings': analytic.cancelled_bookings,
            'available_vendors': analytic.available_vendors,
            'active_vendors': analytic.active_vendors,
            'avg_response_time_minutes': analytic.avg_response_time_minutes,
            'avg_completion_time_hours': analytic.avg_completion_time_hours,
            'customer_satisfaction_avg': analytic.customer_satisfaction_avg,
            'total_revenue': float(analytic.total_revenue),
            'avg_booking_value': float(analytic.avg_booking_value) if analytic.avg_booking_value else 0,
            'demand_ratio': analytic.demand_ratio,
            'is_high_demand': analytic.is_high_demand,
            'is_low_vendor_count': analytic.is_low_vendor_count,
            'alerts_sent': {
                'high_demand': analytic.high_demand_alert_sent,
                'low_vendor': analytic.low_vendor_alert_sent,
                'promotional': analytic.promotional_alert_sent
            }
        })
    
    # Summary statistics
    summary = {
        'total_pincodes': queryset.values('pincode').distinct().count(),
        'high_demand_areas': queryset.filter(total_bookings__gt=5).count(),
        'low_vendor_areas': queryset.filter(available_vendors__lt=2).count(),
        'avg_bookings_per_pincode': queryset.aggregate(Avg('total_bookings'))['total_bookings__avg'] or 0,
        'total_revenue': float(queryset.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0)
    }
    
    return Response({
        'status': 'success',
        'analytics': analytics_data,
        'summary': summary,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'total_pages': (total_count + per_page - 1) // per_page
        }
    })