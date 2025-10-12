"""
Celery tasks for automated messaging and business alerts
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, F
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_pincode_analytics():
    """Generate daily pincode analytics data"""
    from .models import Booking, User, PincodeAnalytics, Service
    
    try:
        today = timezone.now().date()
        
        # Get all pincodes with activity
        active_pincodes = set()
        
        # Pincodes from bookings
        booking_pincodes = Booking.objects.values_list('pincode', flat=True).distinct()
        active_pincodes.update(booking_pincodes)
        
        # Pincodes from vendors
        vendor_pincodes = User.objects.filter(
            role='vendor', 
            is_active=True
        ).values_list('pincode', flat=True).distinct()
        active_pincodes.update(vendor_pincodes)
        
        # Remove empty pincodes
        active_pincodes = {pc for pc in active_pincodes if pc}
        
        logger.info(f"Processing analytics for {len(active_pincodes)} pincodes")
        
        for pincode in active_pincodes:
            try:
                # Get or create analytics record for today
                analytics, created = PincodeAnalytics.objects.get_or_create(
                    pincode=pincode,
                    date=today,
                    defaults={}
                )
                
                # Calculate booking metrics
                today_bookings = Booking.objects.filter(
                    pincode=pincode,
                    created_at__date=today
                )
                
                analytics.total_bookings = today_bookings.count()
                analytics.pending_bookings = today_bookings.filter(status='pending').count()
                analytics.completed_bookings = today_bookings.filter(status='completed').count()
                analytics.cancelled_bookings = today_bookings.filter(status='cancelled').count()
                
                # Calculate vendor metrics
                vendors_in_pincode = User.objects.filter(
                    role='vendor',
                    pincode=pincode,
                    is_active=True
                )
                analytics.available_vendors = vendors_in_pincode.filter(is_available=True).count()
                
                # Vendors who took bookings today
                active_vendor_ids = today_bookings.filter(
                    vendor__isnull=False
                ).values_list('vendor_id', flat=True).distinct()
                analytics.active_vendors = len(active_vendor_ids)
                
                # Calculate performance metrics
                completed_today = today_bookings.filter(
                    status__in=['completed', 'signed'],
                    completion_date__isnull=False
                )
                
                if completed_today.exists():
                    # Average response time (from creation to vendor assignment)
                    response_times = []
                    for booking in completed_today.filter(vendor__isnull=False):
                        if booking.vendor and booking.created_at:
                            # Approximate response time (we'd need a vendor_assigned_at field for accuracy)
                            response_time = (booking.scheduled_date - booking.created_at).total_seconds() / 60
                            if response_time > 0:
                                response_times.append(response_time)
                    
                    if response_times:
                        analytics.avg_response_time_minutes = sum(response_times) / len(response_times)
                    
                    # Average completion time
                    completion_times = []
                    for booking in completed_today:
                        if booking.completion_date and booking.scheduled_date:
                            completion_time = (booking.completion_date - booking.scheduled_date).total_seconds() / 3600
                            if completion_time > 0:
                                completion_times.append(completion_time)
                    
                    if completion_times:
                        analytics.avg_completion_time_hours = sum(completion_times) / len(completion_times)
                    
                    # Customer satisfaction average
                    from .models import Signature
                    signatures = Signature.objects.filter(
                        booking__in=completed_today,
                        status='signed',
                        satisfaction_rating__isnull=False
                    )
                    if signatures.exists():
                        analytics.customer_satisfaction_avg = signatures.aggregate(
                            avg_rating=Avg('satisfaction_rating')
                        )['avg_rating']
                
                # Calculate revenue metrics
                completed_bookings_today = today_bookings.filter(status__in=['completed', 'signed'])
                if completed_bookings_today.exists():
                    revenue_data = completed_bookings_today.aggregate(
                        total=Sum('total_price'),
                        avg=Avg('total_price')
                    )
                    analytics.total_revenue = revenue_data['total'] or Decimal('0')
                    analytics.avg_booking_value = revenue_data['avg'] or Decimal('0')
                
                analytics.save()
                
                if created:
                    logger.info(f"Created new analytics record for pincode {pincode} on {today}")
                else:
                    logger.info(f"Updated analytics record for pincode {pincode} on {today}")
                    
            except Exception as pincode_error:
                logger.error(f"Error processing analytics for pincode {pincode}: {str(pincode_error)}")
                continue
        
        logger.info(f"Completed pincode analytics generation for {today}")
        return f"Processed {len(active_pincodes)} pincodes"
        
    except Exception as e:
        logger.error(f"Error in generate_pincode_analytics: {str(e)}")
        raise


@shared_task
def send_pincode_demand_alerts():
    """Send demand-based notifications to vendors"""
    from .models import PincodeAnalytics, NotificationLog
    from .notification_service import NotificationService
    
    try:
        today = timezone.now().date()
        
        # Get high-demand pincodes that haven't been alerted today
        high_demand_areas = PincodeAnalytics.objects.filter(
            date=today,
            high_demand_alert_sent=False
        ).filter(
            Q(total_bookings__gt=5) |  # More than 5 bookings
            Q(total_bookings__gt=F('available_vendors') * 3)  # 3+ bookings per vendor
        )
        
        alert_count = 0
        for analytics in high_demand_areas:
            try:
                demand_data = {
                    'total_bookings': analytics.total_bookings,
                    'available_vendors': analytics.available_vendors,
                    'avg_booking_value': float(analytics.avg_booking_value) if analytics.avg_booking_value else 0,
                    'demand_ratio': analytics.demand_ratio,
                }
                
                # Send demand notifications
                success = NotificationService.send_demand_notifications(
                    analytics.pincode, 
                    demand_data
                )
                
                if success:
                    analytics.high_demand_alert_sent = True
                    analytics.save()
                    alert_count += 1
                    logger.info(f"Sent demand alerts for high-demand pincode {analytics.pincode}")
                
            except Exception as area_error:
                logger.error(f"Error sending demand alert for {analytics.pincode}: {str(area_error)}")
                continue
        
        return f"Sent demand alerts for {alert_count} high-demand areas"
        
    except Exception as e:
        logger.error(f"Error in send_pincode_demand_alerts: {str(e)}")
        raise


@shared_task
def send_vendor_bonus_alerts():
    """Send bonus alerts to vendors in high-demand areas"""
    from .models import PincodeAnalytics
    from .notification_service import NotificationService
    
    try:
        today = timezone.now().date()
        
        # Get very high-demand areas for bonus alerts
        bonus_areas = PincodeAnalytics.objects.filter(
            date=today,
            total_bookings__gt=8,  # Very high demand
            available_vendors__lt=3  # Low vendor count
        ).exclude(
            high_demand_alert_sent=True  # Don't double-alert the same day
        )
        
        alert_count = 0
        bonus_percentage = 15  # 15% bonus for very high demand
        
        for analytics in bonus_areas:
            try:
                success = NotificationService.send_bonus_alerts(
                    analytics.pincode, 
                    bonus_percentage
                )
                
                if success:
                    alert_count += 1
                    logger.info(f"Sent bonus alerts for pincode {analytics.pincode} ({bonus_percentage}% bonus)")
                
            except Exception as area_error:
                logger.error(f"Error sending bonus alert for {analytics.pincode}: {str(area_error)}")
                continue
        
        return f"Sent bonus alerts for {alert_count} areas"
        
    except Exception as e:
        logger.error(f"Error in send_vendor_bonus_alerts: {str(e)}")
        raise


@shared_task
def send_promotional_campaigns():
    """Send promotional campaigns to customers in specific areas"""
    from .models import PincodeAnalytics
    from .notification_service import NotificationService
    
    try:
        today = timezone.now().date()
        
        # Get areas with low activity for promotional campaigns
        low_activity_areas = PincodeAnalytics.objects.filter(
            date=today,
            total_bookings__lt=3,  # Low booking activity
            promotional_alert_sent=False
        )
        
        promotion_data = {
            'subject': '🎯 Special Offer in Your Area!',
            'title': 'Exclusive Weekend Offer',
            'description': 'Book any home service this weekend and save big!',
            'offer_text': '25% OFF',
            'offer_description': 'On all home services this weekend',
            'action_text': 'Book Now & Save',
            'action_url': 'https://app.homeservepro.com/book',
            'expiry_date': (today + timedelta(days=3)).strftime('%B %d, %Y'),
        }
        
        campaign_count = 0
        for analytics in low_activity_areas:
            try:
                success = NotificationService.location_based_promotions(
                    analytics.pincode, 
                    promotion_data
                )
                
                if success:
                    analytics.promotional_alert_sent = True
                    analytics.save()
                    campaign_count += 1
                    logger.info(f"Sent promotional campaign to pincode {analytics.pincode}")
                
            except Exception as area_error:
                logger.error(f"Error sending promotional campaign for {analytics.pincode}: {str(area_error)}")
                continue
        
        return f"Sent promotional campaigns to {campaign_count} areas"
        
    except Exception as e:
        logger.error(f"Error in send_promotional_campaigns: {str(e)}")
        raise


@shared_task
def check_pending_signatures():
    """Check for signatures pending more than 24 hours"""
    from .models import Signature, BusinessAlert
    from .notification_service import NotificationService
    
    try:
        # Check signatures pending for more than 24 hours
        threshold_time = timezone.now() - timedelta(hours=24)
        
        pending_signatures = Signature.objects.filter(
            status='pending',
            requested_at__lt=threshold_time
        ).select_related('booking', 'booking__customer', 'booking__vendor')
        
        if not pending_signatures.exists():
            return "No pending signatures requiring alerts"
        
        # Group by time ranges for better reporting
        critical_signatures = pending_signatures.filter(
            requested_at__lt=timezone.now() - timedelta(hours=48)
        )
        
        alert_data = {
            'total_pending': pending_signatures.count(),
            'critical_pending': critical_signatures.count(),
            'oldest_request': pending_signatures.order_by('requested_at').first().requested_at.strftime('%Y-%m-%d %H:%M'),
            'items': [
                f"Booking {sig.booking.id} - {sig.booking.service.name} (Pending {(timezone.now() - sig.requested_at).days} days)"
                for sig in pending_signatures[:10]
            ]
        }
        
        # Create business alert
        business_alert = BusinessAlert.objects.create(
            alert_type='pending_signature',
            severity='high' if critical_signatures.exists() else 'medium',
            title=f"{pending_signatures.count()} Signatures Pending",
            description=f"Multiple signatures are pending beyond 24 hours. {critical_signatures.count()} are critical (48+ hours).",
            metadata=alert_data
        )
        
        # Send alert to ops managers
        NotificationService.send_business_alert(
            'pending_signature',
            None,  # Will auto-select ops managers
            alert_data
        )
        
        logger.info(f"Sent pending signature alert for {pending_signatures.count()} signatures")
        return f"Alert sent for {pending_signatures.count()} pending signatures"
        
    except Exception as e:
        logger.error(f"Error in check_pending_signatures: {str(e)}")
        raise


@shared_task
def check_payment_holds():
    """Check for payments stuck in escrow/hold"""
    from .models import Payment, BusinessAlert
    from .notification_service import NotificationService
    
    try:
        # Check payments on hold for more than 24 hours
        threshold_time = timezone.now() - timedelta(hours=24)
        
        held_payments = Payment.objects.filter(
            status='on_hold',
            created_at__lt=threshold_time
        ).select_related('booking')
        
        if not held_payments.exists():
            return "No payments requiring hold alerts"
        
        total_amount = sum(payment.amount for payment in held_payments)
        
        alert_data = {
            'total_payments': held_payments.count(),
            'total_amount': float(total_amount),
            'avg_hold_time': f"{((timezone.now() - held_payments.aggregate(avg_time=Avg('created_at'))['avg_time']).total_seconds() / 3600):.1f} hours",
            'items': [
                f"Payment {payment.id} - ₹{payment.amount} (Booking {payment.booking.id})"
                for payment in held_payments[:10]
            ]
        }
        
        # Create business alert
        business_alert = BusinessAlert.objects.create(
            alert_type='payment_hold',
            severity='high',
            title=f"{held_payments.count()} Payments on Hold",
            description=f"₹{total_amount} in payments are stuck in escrow and need attention.",
            metadata=alert_data
        )
        
        # Send alert to ops managers and finance team
        NotificationService.send_business_alert(
            'payment_hold',
            None,
            alert_data
        )
        
        logger.info(f"Sent payment hold alert for {held_payments.count()} payments")
        return f"Alert sent for {held_payments.count()} held payments"
        
    except Exception as e:
        logger.error(f"Error in check_payment_holds: {str(e)}")
        raise


@shared_task
def check_booking_timeouts():
    """Check for bookings that have exceeded expected completion time"""
    from .models import Booking, BusinessAlert
    from .notification_service import NotificationService
    
    try:
        # Check bookings scheduled more than 24 hours ago but not completed
        threshold_time = timezone.now() - timedelta(hours=24)
        
        overdue_bookings = Booking.objects.filter(
            scheduled_date__lt=threshold_time,
            status__in=['confirmed', 'in_progress']
        ).select_related('customer', 'vendor', 'service')
        
        if not overdue_bookings.exists():
            return "No overdue bookings requiring alerts"
        
        # Categorize by severity
        critical_bookings = overdue_bookings.filter(
            scheduled_date__lt=timezone.now() - timedelta(hours=48)
        )
        
        alert_data = {
            'total_overdue': overdue_bookings.count(),
            'critical_overdue': critical_bookings.count(),
            'avg_delay_hours': f"{((timezone.now() - overdue_bookings.aggregate(avg_time=Avg('scheduled_date'))['avg_time']).total_seconds() / 3600):.1f}",
            'items': [
                f"Booking {booking.id} - {booking.service.name} (Overdue {(timezone.now() - booking.scheduled_date).days} days)"
                for booking in overdue_bookings[:10]
            ]
        }
        
        # Create business alert
        business_alert = BusinessAlert.objects.create(
            alert_type='booking_timeout',
            severity='critical' if critical_bookings.exists() else 'high',
            title=f"{overdue_bookings.count()} Overdue Bookings",
            description=f"Multiple bookings are overdue. {critical_bookings.count()} are critically overdue (48+ hours).",
            metadata=alert_data
        )
        
        # Send alert to ops managers
        NotificationService.send_business_alert(
            'booking_timeout',
            None,
            alert_data
        )
        
        logger.info(f"Sent booking timeout alert for {overdue_bookings.count()} bookings")
        return f"Alert sent for {overdue_bookings.count()} overdue bookings"
        
    except Exception as e:
        logger.error(f"Error in check_booking_timeouts: {str(e)}")
        raise


@shared_task
def send_vendor_completion_reminders():
    """Send reminders to vendors about upcoming or overdue service completions"""
    from .models import Booking, NotificationLog
    from .notification_service import NotificationService
    
    try:
        now = timezone.now()
        
        # Get bookings due in next 2 hours or overdue
        upcoming_threshold = now + timedelta(hours=2)
        overdue_threshold = now - timedelta(hours=2)
        
        reminder_bookings = Booking.objects.filter(
            status='in_progress',
            scheduled_date__range=[overdue_threshold, upcoming_threshold],
            vendor__isnull=False
        ).select_related('vendor', 'customer', 'service')
        
        if not reminder_bookings.exists():
            return "No bookings requiring completion reminders"
        
        reminder_count = 0
        for booking in reminder_bookings:
            try:
                # Check if we already sent a reminder today
                today = timezone.now().date()
                existing_reminder = NotificationLog.objects.filter(
                    recipient=booking.vendor,
                    notification_type='service_completion_reminder',
                    sent_at__date=today,
                    metadata__booking_id=str(booking.id)
                ).exists()
                
                if existing_reminder:
                    continue
                
                is_overdue = booking.scheduled_date < now
                subject = f"⏰ Service {'Overdue' if is_overdue else 'Due Soon'} - {booking.service.name}"
                
                # Create reminder message
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: {'#ff4757' if is_overdue else '#ffa502'}; padding: 20px; text-align: center;">
                        <h1 style="color: white; margin: 0;">⏰ Service {'Overdue' if is_overdue else 'Reminder'}</h1>
                    </div>
                    <div style="padding: 30px; background-color: #f8f9fa;">
                        <h2 style="color: #333;">Hello {booking.vendor.get_full_name()},</h2>
                        <p>This is a reminder about your scheduled service:</p>
                        
                        <div style="background: #fff; border: 1px solid #dee2e6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #495057;">Service Details:</h3>
                            <ul style="color: #6c757d;">
                                <li><strong>Service:</strong> {booking.service.name}</li>
                                <li><strong>Customer:</strong> {booking.customer.get_full_name()}</li>
                                <li><strong>Scheduled:</strong> {booking.scheduled_date.strftime('%B %d, %Y at %I:%M %p')}</li>
                                <li><strong>Status:</strong> {booking.get_status_display()}</li>
                                <li><strong>Booking ID:</strong> {booking.id}</li>
                            </ul>
                        </div>
                        
                        <div style="background: {'#ff4757' if is_overdue else '#ffa502'}; color: white; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                            <p style="margin: 0; font-weight: bold;">
                                {'⚠️ This service is overdue! Please complete it immediately.' if is_overdue else '⏰ This service is due soon. Please complete it on time.'}
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <p style="color: #666;">Please log in to your vendor dashboard to update the service status.</p>
                        </div>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                        <p style="color: #999; font-size: 12px;">
                            This is an automated reminder from HomeServe Pro.
                        </p>
                    </div>
                </body>
                </html>
                """
                
                text_message = f"""
                Service {'Overdue' if is_overdue else 'Reminder'}
                
                Hello {booking.vendor.get_full_name()},
                
                This is a reminder about your scheduled service:
                
                Service: {booking.service.name}
                Customer: {booking.customer.get_full_name()}
                Scheduled: {booking.scheduled_date.strftime('%B %d, %Y at %I:%M %p')}
                Booking ID: {booking.id}
                
                {'⚠️ This service is overdue! Please complete it immediately.' if is_overdue else '⏰ Please complete this service on time.'}
                
                Please log in to your vendor dashboard to update the service status.
                
                ---
                HomeServe Pro Team
                """
                
                # Send email
                from django.core.mail import send_mail
                result = send_mail(
                    subject=subject,
                    message=text_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.vendor.email],
                    fail_silently=False
                )
                
                # Log notification
                NotificationLog.objects.create(
                    recipient=booking.vendor,
                    notification_type='service_completion_reminder',
                    method='email',
                    status='sent' if result else 'failed',
                    subject=subject,
                    message=text_message,
                    metadata={
                        'booking_id': str(booking.id),
                        'is_overdue': is_overdue,
                        'scheduled_date': booking.scheduled_date.isoformat()
                    }
                )
                
                if result:
                    reminder_count += 1
                    logger.info(f"Sent completion reminder to {booking.vendor.email} for booking {booking.id}")
                
            except Exception as booking_error:
                logger.error(f"Error sending reminder for booking {booking.id}: {str(booking_error)}")
                continue
        
        return f"Sent completion reminders for {reminder_count} bookings"
        
    except Exception as e:
        logger.error(f"Error in send_vendor_completion_reminders: {str(e)}")
        raise


@shared_task
def cleanup_old_notifications():
    """Clean up old notification logs to prevent database bloat"""
    from .models import NotificationLog, BusinessAlert
    
    try:
        # Delete notification logs older than 90 days
        cutoff_date = timezone.now() - timedelta(days=90)
        
        old_notifications = NotificationLog.objects.filter(sent_at__lt=cutoff_date)
        deleted_count = old_notifications.count()
        old_notifications.delete()
        
        # Archive resolved business alerts older than 30 days
        alert_cutoff = timezone.now() - timedelta(days=30)
        old_alerts = BusinessAlert.objects.filter(
            status='resolved',
            resolved_at__lt=alert_cutoff
        )
        alert_count = old_alerts.count()
        old_alerts.delete()
        
        logger.info(f"Cleaned up {deleted_count} old notifications and {alert_count} old alerts")
        return f"Cleaned up {deleted_count} notifications and {alert_count} alerts"
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_notifications: {str(e)}")
        raise


# Additional task for manual testing
@shared_task
def test_notification_system():
    """Test the notification system with sample data"""
    from .notification_service import NotificationService
    
    try:
        # Test pincode analytics
        generate_pincode_analytics.delay()
        
        # Wait a bit and then test alerts
        from celery import chain
        
        # Chain the tasks
        workflow = chain(
            generate_pincode_analytics.s(),
            send_pincode_demand_alerts.s(),
            send_vendor_bonus_alerts.s(),
            check_pending_signatures.s(),
            check_payment_holds.s(),
            check_booking_timeouts.s()
        )
        
        workflow.delay()
        
        return "Notification system test initiated"
        
    except Exception as e:
        logger.error(f"Error in test_notification_system: {str(e)}")
        raise