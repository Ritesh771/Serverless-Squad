import stripe
from django.conf import settings
from .models import Payment, Booking, Signature
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Set Stripe API key from settings
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class PaymentService:
    """Service for handling Stripe payments"""
    
    @staticmethod
    def create_payment_intent(booking):
        """Create Stripe payment intent"""
        try:
            if not stripe.api_key or stripe.api_key == '':
                logger.warning("Stripe not configured. Creating mock payment intent.")
                # Mock payment intent for development
                return {
                    'id': f'pi_mock_{booking.id}',
                    'client_secret': f'pi_mock_{booking.id}_secret',
                    'amount': int(booking.total_price * 100),
                    'status': 'requires_payment_method',
                    'currency': 'inr'
                }
            
            intent = stripe.PaymentIntent.create(
                amount=int(booking.total_price * 100),  # Convert to paise (cents for INR)
                currency='inr',
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    'booking_id': str(booking.id),
                    'customer_id': str(booking.customer.id),
                    'vendor_id': str(booking.vendor.id) if booking.vendor else '',
                    'service_name': booking.service.name,
                }
            )
            
            # Create payment record
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'amount': booking.total_price,
                    'stripe_payment_intent_id': intent.id,
                    'status': 'pending'
                }
            )
            
            if not created:
                # Update existing payment
                payment.stripe_payment_intent_id = intent.id
                payment.status = 'pending'
                payment.save()
            
            logger.info(f"Payment intent created: {intent.id} for booking {booking.id}")
            return {
                'id': intent.id,
                'client_secret': intent.client_secret,
                'amount': intent.amount,
                'status': intent.status,
                'currency': intent.currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to create payment intent: {str(e)}")
            return None
    
    @staticmethod
    def process_automatic_payment(booking):
        """Process automatic payment when signature is verified"""
        try:
            # Check if signature is verified
            signature = getattr(booking, 'signature', None)
            if not signature or signature.status != 'signed':
                logger.warning(f"Cannot process payment - signature not verified for booking {booking.id}")
                return False
            
            # Get payment record
            payment = getattr(booking, 'payment', None)
            if not payment:
                logger.error(f"No payment record found for booking {booking.id}")
                return False
            
            # If we have a real Stripe payment intent, capture it
            if payment.stripe_payment_intent_id and not payment.stripe_payment_intent_id.startswith('pi_mock'):
                try:
                    # Confirm and capture the payment
                    intent = stripe.PaymentIntent.confirm(
                        payment.stripe_payment_intent_id,
                        payment_method='pm_card_visa',  # Mock payment method for demo
                    )
                    
                    if intent.status == 'succeeded':
                        payment.status = 'completed'
                        payment.stripe_charge_id = intent.latest_charge
                    else:
                        payment.status = 'failed'
                        logger.error(f"Payment failed for booking {booking.id}: {intent.status}")
                        return False
                        
                except stripe.error.StripeError as e:
                    logger.error(f"Stripe error processing payment: {str(e)}")
                    payment.status = 'failed'
                    payment.save()
                    return False
            else:
                # Mock payment processing for development
                payment.status = 'completed'
            
            payment.processed_at = timezone.now()
            payment.save()
            
            # Update booking status
            booking.status = 'signed'
            booking.save()
            
            logger.info(f"Automatic payment processed for booking {booking.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process automatic payment: {str(e)}")
            return False