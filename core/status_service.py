"""
Service for sending real-time booking status updates via WebSockets
"""
import json
import logging
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class BookingStatusService:
    """Service for managing real-time booking status notifications"""
    
    @staticmethod
    def send_status_update(booking, previous_status=None):
        """
        Send booking status update to all relevant parties
        
        Args:
            booking: Booking object
            previous_status: Previous status of the booking (optional)
        """
        try:
            channel_layer = get_channel_layer()
            
            # Prepare status update data
            status_data = {
                'booking_id': str(booking.id),
                'status': booking.status,
                'previous_status': previous_status,
                'timestamp': timezone.now().isoformat(),
                'message': f'Booking status updated to {booking.get_status_display()}',
                'service_name': booking.service.name if booking.service else 'Unknown Service'
            }
            
            # Send to booking-specific group
            async_to_sync(channel_layer.group_send)(
                f'status_booking_{booking.id}',
                {
                    'type': 'booking_status_update',
                    'booking_id': str(booking.id),
                    'status': booking.status,
                    'previous_status': previous_status,
                    'timestamp': timezone.now().isoformat(),
                    'message': f'Booking status updated to {booking.get_status_display()}',
                    'service_name': booking.service.name if booking.service else 'Unknown Service'
                }
            )
            
            # Send to customer
            if booking.customer:
                async_to_sync(channel_layer.group_send)(
                    f'status_user_{booking.customer.id}',
                    {
                        'type': 'booking_status_update',
                        'booking_id': str(booking.id),
                        'status': booking.status,
                        'previous_status': previous_status,
                        'timestamp': timezone.now().isoformat(),
                        'message': f'Your {booking.service.name} booking status updated to {booking.get_status_display()}',
                        'service_name': booking.service.name if booking.service else 'Unknown Service'
                    }
                )
            
            # Send to vendor if assigned
            if booking.vendor:
                async_to_sync(channel_layer.group_send)(
                    f'status_user_{booking.vendor.id}',
                    {
                        'type': 'booking_status_update',
                        'booking_id': str(booking.id),
                        'status': booking.status,
                        'previous_status': previous_status,
                        'timestamp': timezone.now().isoformat(),
                        'message': f'{booking.service.name} booking status updated to {booking.get_status_display()}',
                        'service_name': booking.service.name if booking.service else 'Unknown Service'
                    }
                )
            
            # Send to ops managers
            async_to_sync(channel_layer.group_send)(
                'status_role_ops_manager',
                {
                    'type': 'booking_status_update',
                    'booking_id': str(booking.id),
                    'status': booking.status,
                    'previous_status': previous_status,
                    'timestamp': timezone.now().isoformat(),
                    'message': f'{booking.service.name} booking status updated to {booking.get_status_display()}',
                    'service_name': booking.service.name if booking.service else 'Unknown Service',
                    'customer_name': booking.customer.get_full_name() if booking.customer else 'Unknown Customer',
                    'vendor_name': booking.vendor.get_full_name() if booking.vendor else 'No Vendor Assigned'
                }
            )
            
            logger.info(f"Status update sent for booking {booking.id}: {previous_status} -> {booking.status}")
            
        except Exception as e:
            logger.error(f"Failed to send status update for booking {booking.id}: {str(e)}")
    
    @staticmethod
    def send_eta_update(booking, eta_minutes):
        """
        Send ETA update to customer
        
        Args:
            booking: Booking object
            eta_minutes: Estimated time of arrival in minutes
        """
        try:
            channel_layer = get_channel_layer()
            
            # Prepare ETA update data
            eta_data = {
                'booking_id': str(booking.id),
                'eta_minutes': eta_minutes,
                'timestamp': timezone.now().isoformat(),
                'message': f'Vendor is estimated to arrive in {eta_minutes} minutes'
            }
            
            # Send to customer
            if booking.customer:
                async_to_sync(channel_layer.group_send)(
                    f'status_user_{booking.customer.id}',
                    {
                        'type': 'booking_eta_update',
                        'booking_id': str(booking.id),
                        'eta_minutes': eta_minutes,
                        'timestamp': timezone.now().isoformat(),
                        'message': f'Vendor is estimated to arrive in {eta_minutes} minutes'
                    }
                )
            
            # Also send to booking-specific group
            async_to_sync(channel_layer.group_send)(
                f'status_booking_{booking.id}',
                {
                    'type': 'booking_eta_update',
                    'booking_id': str(booking.id),
                    'eta_minutes': eta_minutes,
                    'timestamp': timezone.now().isoformat(),
                    'message': f'Vendor is estimated to arrive in {eta_minutes} minutes'
                }
            )
            
            logger.info(f"ETA update sent for booking {booking.id}: {eta_minutes} minutes")
            
        except Exception as e:
            logger.error(f"Failed to send ETA update for booking {booking.id}: {str(e)}")
    
    @staticmethod
    def send_vendor_location_update(booking, latitude, longitude):
        """
        Send vendor location update to customer
        
        Args:
            booking: Booking object
            latitude: Vendor's current latitude
            longitude: Vendor's current longitude
        """
        try:
            channel_layer = get_channel_layer()
            
            # Prepare location update data
            location_data = {
                'booking_id': str(booking.id),
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': timezone.now().isoformat(),
                'message': 'Vendor location updated'
            }
            
            # Send to customer
            if booking.customer:
                async_to_sync(channel_layer.group_send)(
                    f'status_user_{booking.customer.id}',
                    {
                        'type': 'booking_location_update',
                        'booking_id': str(booking.id),
                        'latitude': latitude,
                        'longitude': longitude,
                        'timestamp': timezone.now().isoformat(),
                        'message': 'Vendor is on the way to your location'
                    }
                )
            
            # Also send to booking-specific group
            async_to_sync(channel_layer.group_send)(
                f'status_booking_{booking.id}',
                {
                    'type': 'booking_location_update',
                    'booking_id': str(booking.id),
                    'latitude': latitude,
                    'longitude': longitude,
                    'timestamp': timezone.now().isoformat(),
                    'message': 'Vendor is on the way to your location'
                }
            )
            
            logger.info(f"Location update sent for booking {booking.id}: ({latitude}, {longitude})")
            
        except Exception as e:
            logger.error(f"Failed to send location update for booking {booking.id}: {str(e)}")