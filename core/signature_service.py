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
            
            # Send notification to customer
            try:
                from .notification_service import NotificationService
                signature_link = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/signature/{signature.id}"
                notification_sent = NotificationService.send_signature_notification(booking, signature_link)
                
                if notification_sent:
                    logger.info(f"Signature notification sent for booking {booking.id}")
                else:
                    logger.warning(f"Failed to send signature notification for booking {booking.id}")
            except Exception as e:
                logger.error(f"Error sending signature notification: {str(e)}")
            
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
            
            logger.info(f"Booking {signature.booking.id} signed by customer {customer.username}")
            return signature
            
        except Signature.DoesNotExist:
            logger.error(f"Signature {signature_id} not found or unauthorized")
            return None
        except Exception as e:
            logger.error(f"Failed to sign booking: {str(e)}")
            return None