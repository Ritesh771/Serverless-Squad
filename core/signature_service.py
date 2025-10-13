from .models import Signature, Booking
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import hashlib
import uuid
import logging

logger = logging.getLogger(__name__)


class SignatureService:
    """Service for handling digital signatures"""
    
    @staticmethod
    def request_signature(booking, requested_by):
        """Request digital signature from customer"""
        try:
            # Check if booking is completed
            if booking.status != 'completed':
                logger.warning(f"Cannot request signature - booking {booking.id} not completed")
                return None
            
            # Check if signature already exists
            existing_signature = getattr(booking, 'signature', None)
            if existing_signature:
                if existing_signature.status == 'signed':
                    logger.info(f"Signature already exists for booking {booking.id}")
                    return existing_signature
                elif existing_signature.status == 'pending':
                    logger.info(f"Signature request already pending for booking {booking.id}")
                    return existing_signature
            
            # Create new signature request
            signature = Signature.objects.create(
                booking=booking,
                expires_at=timezone.now() + timedelta(hours=48)  # 48 hours expiry
            )
            
            # Try to use DocuSign if available
            docusign_envelope_id = None
            docusign_signing_url = None
            
            try:
                from .docusign_service import get_docusign_service
                docusign_service = get_docusign_service()
                
                if docusign_service:
                    # Create DocuSign envelope
                    envelope_id = docusign_service.create_signature_envelope(
                        booking,
                        booking.customer.email,
                        booking.customer.get_full_name()
                    )
                    
                    # Update signature with DocuSign info
                    signature.docusign_envelope_id = envelope_id
                    # In a real implementation, you would get the signing URL from DocuSign
                    # signature.docusign_signing_url = signing_url
                    signature.save()
                    
                    docusign_envelope_id = envelope_id
                    logger.info(f"DocuSign envelope created for booking {booking.id}: {envelope_id}")
                    
            except Exception as e:
                logger.warning(f"DocuSign integration failed, falling back to email notification: {str(e)}")
            
            # Send notification to customer
            try:
                from .notification_service import NotificationService
                if docusign_envelope_id and docusign_signing_url:
                    # Use DocuSign signing URL
                    signature_link = docusign_signing_url
                else:
                    # Fallback to local signature page
                    signature_link = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/signature/{signature.id}"
                
                notification_sent = NotificationService.send_signature_notification(booking, signature_link)
                
                if notification_sent:
                    logger.info(f"Signature notification sent for booking {booking.id}")
                else:
                    logger.warning(f"Failed to send signature notification for booking {booking.id}")
            except Exception as e:
                logger.error(f"Error sending signature notification: {str(e)}")
            
            # Send WebSocket notification
            try:
                SignatureService._send_signature_notification('signature_requested', booking, signature)
            except Exception as e:
                logger.error(f"Error sending WebSocket signature notification: {str(e)}")
            
            logger.info(f"Signature requested for booking {booking.id} by {requested_by.username}")
            return signature
            
        except Exception as e:
            logger.error(f"Failed to request signature: {str(e)}")
            return None
    
    @staticmethod
    def sign_booking(signature_id, customer, satisfaction_rating=None, comments=None):
        """Sign booking with customer satisfaction"""
        try:
            signature = Signature.objects.get(id=signature_id, booking__customer=customer)
            
            # Check if already signed
            if signature.status == 'signed':
                logger.info(f"Signature {signature_id} already signed")
                return signature
            
            # Check if expired
            if timezone.now() > signature.expires_at:
                signature.status = 'expired'
                signature.save()
                logger.warning(f"Signature {signature_id} expired")
                return None
            
            # Sign the booking
            signature.signed_by = customer
            signature.signed_at = timezone.now()
            signature.status = 'signed'
            signature.satisfaction_rating = satisfaction_rating
            signature.satisfaction_comments = comments or ''
            
            # Create signature data for hashing
            signature_data = {
                'booking_id': str(signature.booking.id),
                'customer_id': str(customer.id),
                'signed_at': signature.signed_at.isoformat(),
                'satisfaction_rating': satisfaction_rating,
                'vendor_id': str(signature.booking.vendor.id) if signature.booking.vendor else ''
            }
            signature.signature_data = signature_data
            
            # Generate hash (done in model save method)
            signature.save()
            
            # Trigger automatic payment processing
            from .payment_service import PaymentService
            PaymentService.process_automatic_payment(signature.booking)
            
            # Send WebSocket notification
            try:
                SignatureService._send_signature_notification('signature_completed', signature.booking, signature)
            except Exception as e:
                logger.error(f"Error sending WebSocket signature completion notification: {str(e)}")
            
            logger.info(f"Booking {signature.booking.id} signed by customer {customer.username}")
            return signature
            
        except Signature.DoesNotExist:
            logger.error(f"Signature {signature_id} not found or unauthorized")
            return None
        except Exception as e:
            logger.error(f"Failed to sign booking: {str(e)}")
            return None
    
    @staticmethod
    def _send_signature_notification(event_type, booking, signature):
        """Send WebSocket notification for signature events"""
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
                'signature_id': str(signature.id),
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
    
    @staticmethod
    def handle_docusign_webhook(payload):
        """Handle DocuSign webhook events"""
        try:
            from .docusign_service import get_docusign_service
            docusign_service = get_docusign_service()
            
            if docusign_service:
                return docusign_service.handle_webhook_event(payload)
            else:
                logger.warning("DocuSign service not available to handle webhook")
                return False
                
        except Exception as e:
            logger.error(f"Error handling DocuSign webhook: {str(e)}")
            return False