from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

from .models import (
    User, Service, Booking, Photo, Signature, Payment, AuditLog,
    VendorAvailability, TravelTimeCache
)
from .serializers import (
    UserSerializer, ServiceSerializer, BookingSerializer,
    PhotoSerializer, SignatureSerializer, PaymentSerializer, AuditLogSerializer,
    VendorAvailabilitySerializer
)
from .permissions import (
    IsCustomer, IsVendor, IsOnboardManager, IsOpsManager, 
    IsSuperAdmin, IsAdminUser, IsOwnerOrAdmin
)
from .utils import AuditLogger
from .payment_service import PaymentService
from .signature_service import SignatureService
from .scheduling_service import scheduling_service
from .travel_service import travel_service
from .dynamic_pricing_service import DynamicPricingService


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'is_verified', 'pincode']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return User.objects.all()
        elif user.role in ['onboard_manager', 'ops_manager']:
            return User.objects.filter(role__in=['customer', 'vendor'])
        else:
            return User.objects.filter(id=user.id)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_active']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'pincode', 'scheduled_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Booking.objects.filter(customer=user)
        elif user.role == 'vendor':
            return Booking.objects.filter(vendor=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return Booking.objects.all()
        else:
            return Booking.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == 'customer':
            booking = serializer.save(customer=self.request.user)
            
            # Apply smart buffering if vendor is assigned
            if booking.vendor and booking.pincode:
                self._apply_smart_buffering(booking)
            
        AuditLogger.log_action(
            user=self.request.user,
            action='create',
            resource_type='Booking',
            resource_id=booking.id,
            request=self.request
        )
    
    def _apply_smart_buffering(self, booking):
        """Apply smart buffering calculations to a booking"""
        try:
            # Get travel time to customer location
            vendor_pincode = booking.vendor.pincode
            if not vendor_pincode:
                # Try to get from vendor availability
                availability = VendorAvailability.objects.filter(
                    vendor=booking.vendor, is_active=True
                ).first()
                if availability:
                    vendor_pincode = availability.primary_pincode
            
            if vendor_pincode:
                travel_data = travel_service.get_travel_time(vendor_pincode, booking.pincode)
                booking.travel_time_to_location_minutes = travel_data['duration_minutes']
                
                # For return trip, assume same travel time (could be optimized later)
                booking.travel_time_from_location_minutes = travel_data['duration_minutes']
            
            # Set estimated service duration from service model
            booking.estimated_service_duration_minutes = booking.service.duration_minutes
            
            # Get vendor's preferred buffer time
            availability = VendorAvailability.objects.filter(
                vendor=booking.vendor, is_active=True
            ).first()
            
            if availability:
                booking.buffer_before_minutes = availability.preferred_buffer_minutes
                booking.buffer_after_minutes = availability.preferred_buffer_minutes
            
            booking.save()
            
        except Exception as e:
            # Log error but don't fail the booking creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Smart buffering failed for booking {booking.id}: {e}")
    
    @action(detail=True, methods=['post'], permission_classes=[IsVendor])
    def accept_booking(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk, status='pending')
        booking.vendor = request.user
        booking.status = 'confirmed'
        booking.save()
        
        AuditLogger.log_action(
            user=request.user, action='update', resource_type='Booking',
            resource_id=booking.id, request=request
        )
        
        # Send WebSocket notification
        try:
            self._send_booking_notification('booking_approved', booking)
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {str(e)}")
        
        return Response({'message': 'Booking accepted successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsVendor])
    def complete_booking(self, request, pk=None):
        """Mark booking as completed by vendor"""
        booking = get_object_or_404(Booking, pk=pk, vendor=request.user, status='in_progress')
        booking.status = 'completed'
        booking.completion_date = timezone.now()
        booking.save()
        
        # Create payment intent
        payment_intent = PaymentService.create_payment_intent(booking)
        
        return Response({
            'message': 'Booking completed successfully',
            'payment_intent': payment_intent
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsVendor])
    def request_signature(self, request, pk=None):
        """Request customer signature for completed booking"""
        booking = get_object_or_404(Booking, pk=pk, vendor=request.user)
        
        signature = SignatureService.request_signature(booking, request.user)
        if signature:
            return Response({
                'message': 'Signature requested successfully',
                'signature_id': signature.id
            })
        else:
            return Response(
                {'error': 'Failed to request signature'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _send_booking_notification(self, event_type, booking):
        """Send WebSocket notification for booking events"""
        try:
            # Import here to avoid circular imports
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            
            # Prepare notification data
            notification_data = {
                'event_type': event_type,
                'booking_id': str(booking.id),
                'service_name': booking.service.name,
                'customer_id': str(booking.customer.id),
                'customer_name': booking.customer.get_full_name(),
                'vendor_id': str(booking.vendor.id) if booking.vendor else None,
                'vendor_name': booking.vendor.get_full_name() if booking.vendor else None,
                'status': booking.status,
                'timestamp': timezone.now().isoformat()
            }
            
            # Notify customer
            async_to_sync(channel_layer.group_send)(
                f'chat_{booking.customer.id}',
                {
                    'type': 'chat.notification',
                    'notification_type': event_type,
                    'data': notification_data
                }
            )
            
            # Notify vendor if exists
            if booking.vendor:
                async_to_sync(channel_layer.group_send)(
                    f'chat_{booking.vendor.id}',
                    {
                        'type': 'chat.notification',
                        'notification_type': event_type,
                        'data': notification_data
                    }
                )
            
            # Notify ops managers
            async_to_sync(channel_layer.group_send)(
                'role_ops_manager',
                {
                    'type': 'chat.notification',
                    'notification_type': event_type,
                    'data': notification_data
                }
            )
            
            logger.info(f"WebSocket notification sent for {event_type} on booking {booking.id}")
            
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification: {str(e)}")


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Photo.objects.filter(booking__customer=user)
        elif user.role == 'vendor':
            return Photo.objects.filter(booking__vendor=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return Photo.objects.all()
        return Photo.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class SignatureViewSet(viewsets.ModelViewSet):
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Signature.objects.filter(booking__customer=user)
        elif user.role == 'vendor':
            return Signature.objects.filter(booking__vendor=user)
        elif user.role in ['ops_manager', 'super_admin']:
            return Signature.objects.all()
        return Signature.objects.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsCustomer])
    def sign(self, request, pk=None):
        """Sign booking with satisfaction rating"""
        satisfaction_rating = request.data.get('satisfaction_rating')
        comments = request.data.get('comments', '')
        
        if not satisfaction_rating or not (1 <= int(satisfaction_rating) <= 5):
            return Response(
                {'error': 'Satisfaction rating (1-5) is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        signature = SignatureService.sign_booking(
            pk, request.user, int(satisfaction_rating), comments
        )
        
        if signature:
            return Response({
                'message': 'Booking signed successfully',
                'signature_hash': signature.signature_hash
            })
        else:
            return Response(
                {'error': 'Failed to sign booking'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['ops_manager', 'super_admin']:
            return Payment.objects.all()
        elif user.role == 'vendor':
            return Payment.objects.filter(booking__vendor=user)
        elif user.role == 'customer':
            return Payment.objects.filter(booking__customer=user)
        return Payment.objects.none()
    
    @action(detail=True, methods=['post'], permission_classes=[IsOpsManager])
    def process_manual_payment(self, request, pk=None):
        """Process manual payment by ops manager"""
        payment = get_object_or_404(Payment, pk=pk)
        
        success = PaymentService.process_manual_payment(payment.id, request.user)
        
        if success:
            return Response({'message': 'Payment processed successfully'})
        else:
            return Response(
                {'error': 'Failed to process payment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'action', 'resource_type']


class VendorAvailabilityViewSet(viewsets.ModelViewSet):
    """Manage vendor availability schedules"""
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'vendor':
            return VendorAvailability.objects.filter(vendor=self.request.user)
        elif self.request.user.role in ['ops_manager', 'super_admin']:
            return VendorAvailability.objects.all()
        return VendorAvailability.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == 'vendor':
            serializer.save(vendor=self.request.user)


class SmartSchedulingAPIView(APIView):
    """Smart scheduling endpoints for intelligent booking"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get available time slots for a vendor and service"""
        vendor_id = request.query_params.get('vendor_id')
        service_id = request.query_params.get('service_id')
        customer_pincode = request.query_params.get('customer_pincode')
        preferred_date = request.query_params.get('preferred_date')
        
        if not all([vendor_id, service_id, customer_pincode, preferred_date]):
            return Response(
                {'error': 'Missing required parameters: vendor_id, service_id, customer_pincode, preferred_date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            preferred_date_obj = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            available_slots = scheduling_service.get_available_time_slots(
                int(vendor_id), int(service_id), customer_pincode, preferred_date_obj
            )
            
            return Response({
                'available_slots': available_slots,
                'total_slots': len(available_slots)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Get optimal booking suggestion"""
        vendor_id = request.data.get('vendor_id')
        service_id = request.data.get('service_id')
        customer_pincode = request.data.get('customer_pincode')
        preferred_date = request.data.get('preferred_date')
        
        if not all([vendor_id, service_id, customer_pincode, preferred_date]):
            return Response(
                {'error': 'Missing required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            preferred_date_obj = datetime.strptime(preferred_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            optimal_slot = scheduling_service.suggest_optimal_booking_time(
                int(vendor_id), int(service_id), customer_pincode, preferred_date_obj
            )
            
            if optimal_slot:
                return Response({'optimal_slot': optimal_slot})
            else:
                return Response(
                    {'message': 'No available slots found for the specified date'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VendorScheduleOptimizationAPIView(APIView):
    """Vendor schedule optimization and analytics"""
    permission_classes = [IsVendor]
    
    def get(self, request):
        """Get schedule optimization for vendor's specific date"""
        optimization_date = request.query_params.get('date')
        
        if not optimization_date:
            return Response(
                {'error': 'Date parameter is required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date_obj = datetime.strptime(optimization_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            optimization = scheduling_service.optimize_vendor_schedule(
                request.user.id, date_obj
            )
            return Response(optimization)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TravelTimeAPIView(APIView):
    """Travel time calculation endpoints"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get travel time between two pincodes"""
        from_pincode = request.query_params.get('from_pincode')
        to_pincode = request.query_params.get('to_pincode')
        
        if not all([from_pincode, to_pincode]):
            return Response(
                {'error': 'Both from_pincode and to_pincode are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            travel_data = travel_service.get_travel_time(from_pincode, to_pincode)
            return Response(travel_data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DynamicPricingAPIView(APIView):
    """Real-time dynamic pricing based on demand and supply"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dynamic price for a service in a pincode"""
        service_id = request.query_params.get('service_id')
        pincode = request.query_params.get('pincode')
        scheduled_datetime = request.query_params.get('scheduled_datetime')
        
        if not all([service_id, pincode]):
            return Response(
                {'error': 'service_id and pincode are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Parse scheduled datetime if provided
        scheduled_dt = None
        if scheduled_datetime:
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_datetime.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Invalid datetime format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # Calculate dynamic price
            pricing_data = DynamicPricingService.calculate_dynamic_price(
                service, pincode, scheduled_dt
            )
            
            return Response({
                'service': {
                    'id': service.id,
                    'name': service.name,
                    'category': service.category
                },
                'pincode': pincode,
                'pricing': pricing_data,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Get price predictions for multiple days"""
        service_id = request.data.get('service_id')
        pincode = request.data.get('pincode')
        days = request.data.get('days', 7)
        
        if not all([service_id, pincode]):
            return Response(
                {'error': 'service_id and pincode are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = Service.objects.get(id=service_id, is_active=True)
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Get price predictions
            predictions = DynamicPricingService.get_price_prediction(
                service, pincode, int(days)
            )
            
            return Response({
                'service': {
                    'id': service.id,
                    'name': service.name,
                    'category': service.category,
                    'base_price': float(service.base_price)
                },
                'pincode': pincode,
                'predictions': predictions,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def chat_query(request):
    """Handle chat queries and return AI/workflow responses"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        role = data.get('role')
        message = data.get('message')
        
        if not all([user_id, role, message]):
            return JsonResponse({'error': 'Missing required fields: user_id, role, message'}, status=400)
        
        # Get user object
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Process message based on role
        response = process_chat_message(user, role, message)
        
        # Log chat action
        AuditLogger.log_action(
            user=user,
            action='chat_query',
            resource_type='Chat',
            resource_id='chat_query',
            new_values={'message': message, 'response': response}
        )
        
        return JsonResponse({'response': response})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        # Log error action
        try:
            AuditLogger.log_action(
                user=request.user if hasattr(request, 'user') else None,
                action='chat_query_error',
                resource_type='Chat',
                resource_id='chat_query',
                new_values={'error': str(e)}
            )
        except:
            pass
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
def chat_context(request):
    """Provide role-specific context for chat suggestions"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        user_id = request.GET.get('user_id')
        role = request.GET.get('role')
        
        if not all([user_id, role]):
            return JsonResponse({'error': 'Missing required parameters: user_id, role'}, status=400)
        
        # Get user object
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Get context based on role
        context = get_role_context(user, role)
        
        # Log context request
        AuditLogger.log_action(
            user=user,
            action='chat_context',
            resource_type='Chat',
            resource_id='chat_context',
            new_values={'role': role}
        )
        
        return JsonResponse({'context': context})
        
    except Exception as e:
        logger.error(f"Error getting chat context: {str(e)}")
        # Log error action
        try:
            AuditLogger.log_action(
                user=request.user if hasattr(request, 'user') else None,
                action='chat_context_error',
                resource_type='Chat',
                resource_id='chat_context',
                new_values={'error': str(e)}
            )
        except:
            pass
        return JsonResponse({'error': 'Internal server error'}, status=500)


def process_chat_message(user, role, message):
    """Process chat message based on user role and return appropriate response"""
    message_lower = message.lower()
    
    # Handle predefined workflow commands
    if role == 'customer':
        if 'track' in message_lower and 'booking' in message_lower:
            return handle_customer_track_bookings(user)
        elif 'approve' in message_lower and 'signature' in message_lower:
            return handle_customer_approve_signature(user, message)
        elif 'booking' in message_lower and 'detail' in message_lower:
            return handle_customer_booking_details(user, message)
        elif 'my bookings' in message_lower or 'list bookings' in message_lower:
            return handle_customer_track_bookings(user)
    
    elif role == 'vendor':
        if 'upload' in message_lower and 'photo' in message_lower:
            return handle_vendor_upload_photos(user, message)
        elif 'request' in message_lower and 'signature' in message_lower:
            return handle_vendor_request_signature(user, message)
        elif 'calendar' in message_lower or 'schedule' in message_lower:
            return handle_vendor_calendar(user)
        elif 'pending' in message_lower and 'job' in message_lower:
            return handle_vendor_pending_jobs(user)
        elif 'my jobs' in message_lower or 'list jobs' in message_lower:
            return handle_vendor_pending_jobs(user)
    
    elif role in ['admin', 'onboard_manager', 'ops_manager']:
        if 'approve' in message_lower and 'vendor' in message_lower:
            return handle_admin_approve_vendor(user, message)
        elif 'monitor' in message_lower and 'signature' in message_lower:
            return handle_admin_monitor_signatures(user)
        elif 'resolve' in message_lower and 'dispute' in message_lower:
            return handle_admin_resolve_dispute(user, message)
        elif 'pending vendors' in message_lower or 'vendor queue' in message_lower:
            return handle_admin_approve_vendor(user, message)
        elif 'signature' in message_lower and 'pending' in message_lower:
            return handle_admin_monitor_signatures(user)
    
    # Handle workflow action commands
    if message == 'track_bookings':
        if role == 'customer':
            return handle_customer_track_bookings(user)
    elif message == 'view_booking_details':
        if role == 'customer':
            return handle_customer_booking_details(user, "")
    elif message == 'upload_photos':
        if role == 'vendor':
            return handle_vendor_upload_photos(user, "")
    elif message == 'request_signature':
        if role == 'vendor':
            return handle_vendor_request_signature(user, "")
    elif message == 'approve_vendor':
        if role in ['admin', 'onboard_manager']:
            return handle_admin_approve_vendor(user, "")
    elif message == 'monitor_signatures':
        if role in ['admin', 'ops_manager']:
            return handle_admin_monitor_signatures(user)
    
    # Default AI-like response for unrecognized queries
    return generate_ai_response(message, role)


def get_role_context(user, role):
    """Get role-specific context for chat suggestions"""
    context = {
        'role': role,
        'suggested_actions': [],
        'recent_activities': []
    }
    
    if role == 'customer':
        # Get customer's bookings
        bookings = Booking.objects.filter(customer=user).order_by('-created_at')[:5]
        context['suggested_actions'] = [
            'Track my bookings',
            'Approve signature for completed service',
            'View booking details'
        ]
        context['recent_activities'] = [
            {
                'type': 'booking',
                'id': str(booking.id),
                'service': booking.service.name,
                'status': booking.get_status_display(),
                'date': booking.scheduled_date.isoformat()
            }
            for booking in bookings
        ]
    
    elif role == 'vendor':
        # Get vendor's bookings
        bookings = Booking.objects.filter(vendor=user).order_by('-created_at')[:5]
        context['suggested_actions'] = [
            'Upload photos for service',
            'Request signature from customer',
            'View my calendar',
            'Check pending jobs'
        ]
        context['recent_activities'] = [
            {
                'type': 'booking',
                'id': str(booking.id),
                'service': booking.service.name,
                'status': booking.get_status_display(),
                'date': booking.scheduled_date.isoformat()
            }
            for booking in bookings
        ]
    
    elif role in ['admin', 'onboard_manager', 'ops_manager']:
        # Get pending vendors for onboard managers
        if role == 'onboard_manager':
            pending_vendors = User.objects.filter(role='vendor', is_verified=False)[:5]
            context['suggested_actions'] = [
                'Approve pending vendors',
                'Review vendor applications',
                'View vendor queue'
            ]
            context['recent_activities'] = [
                {
                    'type': 'vendor_application',
                    'id': str(vendor.id),
                    'name': vendor.get_full_name(),
                    'date': vendor.date_joined.isoformat()
                }
                for vendor in pending_vendors
            ]
        else:
            # For ops managers and admins
            pending_signatures = Signature.objects.filter(status='pending')[:5]
            context['suggested_actions'] = [
                'Monitor pending signatures',
                'Resolve customer disputes',
                'View system analytics'
            ]
            context['recent_activities'] = [
                {
                    'type': 'signature',
                    'id': str(signature.id),
                    'booking_id': str(signature.booking.id),
                    'customer': signature.booking.customer.get_full_name(),
                    'date': signature.requested_at.isoformat()
                }
                for signature in pending_signatures
            ]
    
    return context


# Workflow handlers for each role
def handle_customer_track_bookings(user):
    """Handle customer request to track bookings"""
    bookings = Booking.objects.filter(customer=user).order_by('-created_at')[:5]
    
    if not bookings:
        return "You don't have any bookings yet. Would you like to book a service?"
    
    response = "Here are your recent bookings:\n\n"
    for booking in bookings:
        response += f"• {booking.service.name} - {booking.get_status_display()}\n"
        response += f"  Scheduled for: {booking.scheduled_date.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"  Booking ID: {booking.id}\n\n"
    
    return response


def handle_customer_approve_signature(user, message):
    """Handle customer request to approve signature"""
    # Extract booking ID from message if provided
    # In a real implementation, this would parse the message to find booking ID
    return "To approve a signature, please visit the 'My Bookings' page and click on 'Sign' for the completed service. You'll be asked to provide a satisfaction rating (1-5) and any comments."


def handle_customer_booking_details(user, message):
    """Handle customer request for booking details"""
    # Extract booking ID from message if provided
    return "To view booking details, please go to the 'My Bookings' page and click on any booking to see its details including service information, scheduled time, and status."


def handle_vendor_upload_photos(user, message):
    """Handle vendor request to upload photos"""
    return "To upload photos, go to the 'My Jobs' page, select a booking, and use the 'Upload Photos' option. You can upload 'before' and 'after' photos of your work."


def handle_vendor_request_signature(user, message):
    """Handle vendor request to request signature"""
    # Get completed bookings without signatures
    bookings = Booking.objects.filter(
        vendor=user, 
        status='completed'
    ).exclude(signature__isnull=False)[:3]
    
    if not bookings:
        return "You don't have any completed bookings that require signatures."
    
    response = "You can request signatures for these completed bookings:\n\n"
    for booking in bookings:
        response += f"• {booking.service.name} for {booking.customer.get_full_name()}\n"
        response += f"  Booking ID: {booking.id}\n"
        response += f"  Completed on: {booking.completion_date.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    response += "To request a signature, go to the booking details page and click 'Request Signature'."
    return response


def handle_vendor_calendar(user):
    """Handle vendor request to view calendar"""
    return "To view your calendar, go to the 'Calendar' page where you can see all your scheduled bookings and their statuses."


def handle_vendor_pending_jobs(user):
    """Handle vendor request to check pending jobs"""
    pending_bookings = Booking.objects.filter(
        vendor=user,
        status__in=['confirmed', 'in_progress']
    ).order_by('scheduled_date')
    
    if not pending_bookings:
        return "You don't have any pending jobs at the moment."
    
    response = "Your pending jobs:\n\n"
    for booking in pending_bookings:
        response += f"• {booking.service.name} for {booking.customer.get_full_name()}\n"
        response += f"  Status: {booking.get_status_display()}\n"
        response += f"  Scheduled for: {booking.scheduled_date.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"  Booking ID: {booking.id}\n\n"
    
    return response


def handle_admin_approve_vendor(user, message):
    """Handle admin request to approve vendor"""
    pending_vendors = User.objects.filter(role='vendor', is_verified=False)[:5]
    
    if not pending_vendors:
        return "There are no pending vendor applications to approve."
    
    response = "Pending vendor applications:\n\n"
    for vendor in pending_vendors:
        response += f"• {vendor.get_full_name()} ({vendor.username})\n"
        response += f"  Email: {vendor.email}\n"
        response += f"  Phone: {vendor.phone}\n"
        response += f"  Joined: {vendor.date_joined.strftime('%Y-%m-%d')}\n\n"
    
    response += "To approve vendors, go to the 'Vendor Queue' page in the admin dashboard."
    return response


def handle_admin_monitor_signatures(user):
    """Handle admin request to monitor signatures"""
    pending_signatures = Signature.objects.filter(status='pending')[:5]
    
    if not pending_signatures:
        return "There are no pending signatures at the moment."
    
    response = "Pending signatures:\n\n"
    for signature in pending_signatures:
        response += f"• Booking: {signature.booking.service.name}\n"
        response += f"  Customer: {signature.booking.customer.get_full_name()}\n"
        response += f"  Vendor: {signature.booking.vendor.get_full_name() if signature.booking.vendor else 'N/A'}\n"
        response += f"  Requested: {signature.requested_at.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"  Expires: {signature.expires_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    response += "To manage signatures, go to the 'Signature Vault' page in the operations dashboard."
    return response


def handle_admin_resolve_dispute(user, message):
    """Handle admin request to resolve dispute"""
    disputed_bookings = Booking.objects.filter(status='disputed')[:5]
    
    if not disputed_bookings:
        return "There are no disputed bookings at the moment."
    
    response = "Disputed bookings:\n\n"
    for booking in disputed_bookings:
        response += f"• {booking.service.name}\n"
        response += f"  Customer: {booking.customer.get_full_name()}\n"
        response += f"  Vendor: {booking.vendor.get_full_name() if booking.vendor else 'N/A'}\n"
        response += f"  Disputed on: {booking.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
        response += f"  Booking ID: {booking.id}\n\n"
    
    response += "To resolve disputes, go to the 'Disputes' section in the admin dashboard."
    return response


def generate_ai_response(message, role):
    """Generate AI-like response for general queries"""
    # This is a simple rule-based response generator
    # In a real implementation, this would connect to an AI service
    
    responses = {
        'hello': 'Hello! How can I help you today?',
        'hi': 'Hi there! What can I assist you with?',
        'help': 'I can help you with various tasks based on your role. Try asking about your bookings, service completion, or signature approvals.',
        'thanks': 'You\'re welcome! Is there anything else I can help you with?',
        'thank you': 'You\'re welcome! Let me know if you need any further assistance.'
    }
    
    message_lower = message.lower()
    for key, response in responses.items():
        if key in message_lower:
            return response
    
    # Default response
    role_prompts = {
        'customer': 'As a customer, you can ask me about your bookings, service completion, or signature approvals.',
        'vendor': 'As a vendor, you can ask me about your jobs, uploading photos, requesting signatures, or viewing your calendar.',
        'admin': 'As an admin, you can ask me about vendor approvals, monitoring signatures, or resolving disputes.',
        'onboard_manager': 'As an onboard manager, you can ask me about vendor applications or approval processes.',
        'ops_manager': 'As an operations manager, you can ask me about monitoring signatures, payments, or system analytics.'
    }
    
    return f"I understand you're asking about '{message}'. {role_prompts.get(role, 'I can help with various tasks in the system.')}"