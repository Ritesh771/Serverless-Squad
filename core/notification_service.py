import random
import string
import logging
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


class NotificationService:
    """Enhanced notification service for email and SMS"""
    
    @staticmethod
    def generate_otp(length=6):
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def send_otp_email(email, otp, user_name=""):
        """Send OTP via email"""
        try:
            subject = 'HomeServe Pro - Verification Code'
            
            # Create email context
            context = {
                'otp': otp,
                'user_name': user_name,
                'app_name': getattr(settings, 'APP_NAME', 'HomeServe Pro'),
                'validity_minutes': 5
            }
            
            # Create HTML and text versions
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">HomeServe Pro</h1>
                </div>
                <div style="padding: 30px; background-color: #f8f9fa;">
                    <h2 style="color: #333;">Verification Code</h2>
                    <p>Hello {user_name},</p>
                    <p>Your verification code for HomeServe Pro is:</p>
                    <div style="background: #007bff; color: white; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; border-radius: 5px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #666;">This code is valid for 5 minutes.</p>
                    <p style="color: #666;">If you didn't request this code, please ignore this email.</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 12px;">
                        This is an automated message from HomeServe Pro. Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """
            
            text_message = f"""
            HomeServe Pro - Verification Code
            
            Hello {user_name},
            
            Your verification code is: {otp}
            
            This code is valid for 5 minutes.
            
            If you didn't request this code, please ignore this email.
            
            ---
            HomeServe Pro Team
            """
            
            # Send email
            result = send_mail(
                subject=subject,
                message=text_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            
            if result:
                logger.info(f"OTP email sent successfully to {email}")
                return True
            else:
                logger.error(f"Failed to send OTP email to {email}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_otp_sms(phone_number, otp):
        """Send OTP via SMS using Twilio"""
        try:
            account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
            auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
            from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
            
            if not all([account_sid, auth_token, from_number]):
                logger.warning(f"Twilio credentials not configured. OTP for {phone_number}: {otp}")
                return False
            
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                body=f'Your HomeServe Pro verification code is: {otp}. Valid for 5 minutes. Do not share this code.',
                from_=from_number,
                to=phone_number
            )
            
            logger.info(f"OTP SMS sent successfully to {phone_number}. Message SID: {message.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Twilio error sending OTP to {phone_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send OTP SMS to {phone_number}: {str(e)}")
            return False
    
    @staticmethod
    def store_otp(identifier, otp, ttl=300):  # 5 minutes TTL
        """Store OTP in cache with TTL"""
        cache_key = f"otp_{identifier}"
        cache.set(cache_key, otp, ttl)
        logger.info(f"OTP stored for {identifier} with {ttl}s TTL")
    
    @staticmethod
    def verify_otp(identifier, otp):
        """Verify OTP against cached value"""
        cache_key = f"otp_{identifier}"
        cached_otp = cache.get(cache_key)
        
        if cached_otp and cached_otp == otp:
            # Delete OTP after successful verification
            cache.delete(cache_key)
            logger.info(f"OTP verified successfully for {identifier}")
            return True
        
        logger.warning(f"OTP verification failed for {identifier}")
        return False
    
    @staticmethod
    def send_and_store_otp(identifier, method='email', user_name=""):
        """
        Generate, send, and store OTP
        
        Args:
            identifier: email or phone number
            method: 'email' or 'sms'
            user_name: optional user name for personalization
        """
        otp = NotificationService.generate_otp()
        
        # For development, also log the OTP
        if settings.DEBUG:
            logger.info(f"Generated OTP for {identifier}: {otp}")
        
        # Send OTP based on method
        if method == 'email':
            otp_sent = NotificationService.send_otp_email(identifier, otp, user_name)
        elif method == 'sms':
            otp_sent = NotificationService.send_otp_sms(identifier, otp)
        else:
            logger.error(f"Invalid OTP method: {method}")
            return {'success': False, 'error': 'Invalid method'}
        
        # Store OTP regardless of send status for development
        NotificationService.store_otp(identifier, otp)
        
        return {
            'success': True,
            'otp_sent': otp_sent,
            'method': method,
            'otp': otp if settings.DEBUG else None  # Only return OTP in debug mode
        }
    
    @staticmethod
    def send_signature_notification(booking, signature_link):
        """Send signature request notification to customer"""
        try:
            customer = booking.customer
            service_name = booking.service.name
            vendor_name = booking.vendor.get_full_name() if booking.vendor else "Your service provider"
            
            subject = f'HomeServe Pro - Service Completion Signature Required'
            
            context = {
                'customer_name': customer.get_full_name(),
                'service_name': service_name,
                'vendor_name': vendor_name,
                'booking_id': booking.id,
                'signature_link': signature_link,
                'app_name': getattr(settings, 'APP_NAME', 'HomeServe Pro')
            }
            
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">Service Completed!</h1>
                </div>
                <div style="padding: 30px; background-color: #f8f9fa;">
                    <h2 style="color: #333;">Signature Required</h2>
                    <p>Hello {customer.get_full_name()},</p>
                    <p><strong>{vendor_name}</strong> has completed your <strong>{service_name}</strong> service.</p>
                    <p>To release payment and confirm your satisfaction, please review the service and provide your digital signature.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{signature_link}" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            Review & Sign Service Completion
                        </a>
                    </div>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0; color: #856404;"><strong>Important:</strong> This signature request will expire in 48 hours. Please complete it promptly to ensure your service provider gets paid.</p>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        <strong>Booking ID:</strong> {booking.id}<br>
                        <strong>Service:</strong> {service_name}<br>
                        <strong>Provider:</strong> {vendor_name}
                    </p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 12px;">
                        This is an automated message from HomeServe Pro. If you didn't request this service, please contact support immediately.
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Send email
            result = send_mail(
                subject=subject,
                message=f"Service completed! Please sign: {signature_link}",
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer.email],
                fail_silently=False
            )
            
            if result:
                logger.info(f"Signature notification sent to {customer.email} for booking {booking.id}")
                return True
            else:
                logger.error(f"Failed to send signature notification to {customer.email}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send signature notification: {str(e)}")
            return False

    @staticmethod
    def send_demand_notifications(pincode, demand_data):
        """Send high demand notifications to vendors in specific pincode"""
        from .models import User, NotificationLog
        
        try:
            # Get available vendors in the pincode
            vendors = User.objects.filter(
                role='vendor',
                pincode=pincode,
                is_available=True,
                is_active=True
            )
            
            if not vendors.exists():
                logger.info(f"No available vendors in pincode {pincode} for demand notifications")
                return False
            
            subject = f"High Demand Alert - {pincode} Area"
            
            for vendor in vendors:
                try:
                    html_message = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 20px; text-align: center;">
                            <h1 style="color: white; margin: 0;">🔥 High Demand Alert!</h1>
                        </div>
                        <div style="padding: 30px; background-color: #f8f9fa;">
                            <h2 style="color: #333;">Opportunity in Your Area</h2>
                            <p>Hello {vendor.get_full_name()},</p>
                            <p>There's high demand for services in <strong>{pincode}</strong> area!</p>
                            
                            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                <h3 style="margin-top: 0; color: #856404;">📊 Current Stats:</h3>
                                <ul style="color: #856404; margin: 0;">
                                    <li><strong>{demand_data.get('total_bookings', 0)}</strong> bookings today</li>
                                    <li><strong>{demand_data.get('available_vendors', 0)}</strong> vendors available</li>
                                    <li><strong>₹{demand_data.get('avg_booking_value', 0)}</strong> average booking value</li>
                                </ul>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <p style="font-size: 18px; color: #28a745; margin: 10px 0;"><strong>💰 Earn more today!</strong></p>
                                <p style="color: #666;">Log in to accept bookings and maximize your earnings.</p>
                            </div>
                            
                            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                            <p style="color: #999; font-size: 12px;">
                                This is an automated alert from HomeServe Pro based on demand analysis.
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    text_message = f"""
                    High Demand Alert - {pincode} Area
                    
                    Hello {vendor.get_full_name()},
                    
                    There's high demand for services in {pincode} area!
                    
                    Current Stats:
                    - {demand_data.get('total_bookings', 0)} bookings today
                    - {demand_data.get('available_vendors', 0)} vendors available
                    - ₹{demand_data.get('avg_booking_value', 0)} average booking value
                    
                    💰 Earn more today! Log in to accept bookings.
                    
                    ---
                    HomeServe Pro Team
                    """
                    
                    # Send email
                    result = send_mail(
                        subject=subject,
                        message=text_message,
                        html_message=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[vendor.email],
                        fail_silently=False
                    )
                    
                    # Log notification
                    NotificationLog.objects.create(
                        recipient=vendor,
                        notification_type='demand_notification',
                        method='email',
                        status='sent' if result else 'failed',
                        subject=subject,
                        message=text_message,
                        metadata={
                            'pincode': pincode,
                            'demand_data': demand_data
                        }
                    )
                    
                    if result:
                        logger.info(f"Demand notification sent to vendor {vendor.email} for pincode {pincode}")
                    else:
                        logger.error(f"Failed to send demand notification to vendor {vendor.email}")
                        
                except Exception as vendor_error:
                    logger.error(f"Error sending demand notification to {vendor.email}: {str(vendor_error)}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send demand notifications for pincode {pincode}: {str(e)}")
            return False
    
    @staticmethod
    def send_bonus_alerts(pincode, bonus_percentage=10):
        """Send bonus alerts to vendors in high-demand areas"""
        from .models import User, NotificationLog
        
        try:
            # Get vendors in the pincode
            vendors = User.objects.filter(
                role='vendor',
                pincode=pincode,
                is_active=True
            )
            
            if not vendors.exists():
                logger.info(f"No vendors in pincode {pincode} for bonus alerts")
                return False
            
            subject = f"🎉 {bonus_percentage}% Bonus Available - {pincode} Area"
            
            for vendor in vendors:
                try:
                    html_message = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); padding: 20px; text-align: center;">
                            <h1 style="color: white; margin: 0;">🎉 Special Bonus Available!</h1>
                        </div>
                        <div style="padding: 30px; background-color: #f8f9fa;">
                            <h2 style="color: #333;">Earn Extra Today!</h2>
                            <p>Hello {vendor.get_full_name()},</p>
                            <p>Great news! We're offering a <strong>{bonus_percentage}% bonus</strong> on all completed bookings in <strong>{pincode}</strong> area today!</p>
                            
                            <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                                <h2 style="color: #155724; margin: 0;">💰 {bonus_percentage}% BONUS</h2>
                                <p style="color: #155724; margin: 10px 0; font-size: 16px;">On all completed services today</p>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <p style="font-size: 16px; color: #333;">📍 <strong>Location:</strong> {pincode} area</p>
                                <p style="color: #666;">Complete services today to earn extra income!</p>
                            </div>
                            
                            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                <p style="margin: 0; color: #856404;"><strong>How it works:</strong></p>
                                <ol style="color: #856404; margin: 10px 0;">
                                    <li>Accept bookings in {pincode} area</li>
                                    <li>Complete the service successfully</li>
                                    <li>Get customer signature</li>
                                    <li>Receive your payment + {bonus_percentage}% bonus!</li>
                                </ol>
                            </div>
                            
                            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                            <p style="color: #999; font-size: 12px;">
                                This bonus offer is valid for today only. Terms and conditions apply.
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    text_message = f"""
                    🎉 {bonus_percentage}% Bonus Available - {pincode} Area
                    
                    Hello {vendor.get_full_name()},
                    
                    Great news! We're offering a {bonus_percentage}% bonus on all completed bookings in {pincode} area today!
                    
                    How it works:
                    1. Accept bookings in {pincode} area
                    2. Complete the service successfully
                    3. Get customer signature
                    4. Receive your payment + {bonus_percentage}% bonus!
                    
                    Location: {pincode} area
                    Valid: Today only
                    
                    ---
                    HomeServe Pro Team
                    """
                    
                    # Send email
                    result = send_mail(
                        subject=subject,
                        message=text_message,
                        html_message=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[vendor.email],
                        fail_silently=False
                    )
                    
                    # Log notification
                    NotificationLog.objects.create(
                        recipient=vendor,
                        notification_type='bonus_alert',
                        method='email',
                        status='sent' if result else 'failed',
                        subject=subject,
                        message=text_message,
                        metadata={
                            'pincode': pincode,
                            'bonus_percentage': bonus_percentage
                        }
                    )
                    
                    if result:
                        logger.info(f"Bonus alert sent to vendor {vendor.email} for pincode {pincode}")
                    else:
                        logger.error(f"Failed to send bonus alert to vendor {vendor.email}")
                        
                except Exception as vendor_error:
                    logger.error(f"Error sending bonus alert to {vendor.email}: {str(vendor_error)}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send bonus alerts for pincode {pincode}: {str(e)}")
            return False
    
    @staticmethod
    def location_based_promotions(pincode, promotion_data):
        """Send promotional messages to customers in specific pincode"""
        from .models import User, NotificationLog
        
        try:
            # Get customers in the pincode
            customers = User.objects.filter(
                role='customer',
                pincode=pincode,
                is_active=True
            )
            
            if not customers.exists():
                logger.info(f"No customers in pincode {pincode} for promotional messages")
                return False
            
            subject = promotion_data.get('subject', f"Special Offer - {pincode} Area")
            
            for customer in customers:
                try:
                    html_message = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                            <h1 style="color: white; margin: 0;">🎯 Special Offer for {pincode}!</h1>
                        </div>
                        <div style="padding: 30px; background-color: #f8f9fa;">
                            <h2 style="color: #333;">{promotion_data.get('title', 'Exclusive Offer')}</h2>
                            <p>Hello {customer.get_full_name()},</p>
                            <p>{promotion_data.get('description', 'We have a special offer just for your area!')}</p>
                            
                            <div style="background: #e1f5fe; border: 1px solid #b3e5fc; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center;">
                                <h2 style="color: #01579b; margin: 0;">{promotion_data.get('offer_text', '20% OFF')}</h2>
                                <p style="color: #01579b; margin: 10px 0; font-size: 16px;">{promotion_data.get('offer_description', 'On your next service booking')}</p>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{promotion_data.get('action_url', '#')}" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                                    {promotion_data.get('action_text', 'Book Now')}
                                </a>
                            </div>
                            
                            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                <p style="margin: 0; color: #856404;"><strong>Valid until:</strong> {promotion_data.get('expiry_date', 'Limited time')}</p>
                                <p style="margin: 0; color: #856404;"><strong>Available in:</strong> {pincode} area</p>
                            </div>
                            
                            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                            <p style="color: #999; font-size: 12px;">
                                This offer is exclusive to customers in {pincode}. Terms and conditions apply.
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    text_message = f"""
                    🎯 Special Offer for {pincode}!
                    
                    Hello {customer.get_full_name()},
                    
                    {promotion_data.get('description', 'We have a special offer just for your area!')}
                    
                    Offer: {promotion_data.get('offer_text', '20% OFF')}
                    Details: {promotion_data.get('offer_description', 'On your next service booking')}
                    
                    Valid until: {promotion_data.get('expiry_date', 'Limited time')}
                    Available in: {pincode} area
                    
                    Book now to avail this exclusive offer!
                    
                    ---
                    HomeServe Pro Team
                    """
                    
                    # Send email
                    result = send_mail(
                        subject=subject,
                        message=text_message,
                        html_message=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[customer.email],
                        fail_silently=False
                    )
                    
                    # Log notification
                    NotificationLog.objects.create(
                        recipient=customer,
                        notification_type='promotional',
                        method='email',
                        status='sent' if result else 'failed',
                        subject=subject,
                        message=text_message,
                        metadata={
                            'pincode': pincode,
                            'promotion_data': promotion_data
                        }
                    )
                    
                    if result:
                        logger.info(f"Promotional message sent to customer {customer.email} for pincode {pincode}")
                    else:
                        logger.error(f"Failed to send promotional message to customer {customer.email}")
                        
                except Exception as customer_error:
                    logger.error(f"Error sending promotional message to {customer.email}: {str(customer_error)}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send promotional messages for pincode {pincode}: {str(e)}")
            return False
    
    @staticmethod
    def send_business_alert(alert_type, recipients, alert_data):
        """Send business alerts to ops managers and admins"""
        from .models import User, NotificationLog, BusinessAlert
        
        try:
            # Get recipients if not provided
            if not recipients:
                recipients = User.objects.filter(
                    role__in=['ops_manager', 'super_admin'],
                    is_active=True
                )
            
            if not recipients:
                logger.warning(f"No recipients found for business alert: {alert_type}")
                return False
            
            # Generate alert content based on type
            subject, html_message, text_message = NotificationService._generate_business_alert_content(
                alert_type, alert_data
            )
            
            success_count = 0
            for recipient in recipients:
                try:
                    # Send email
                    result = send_mail(
                        subject=subject,
                        message=text_message,
                        html_message=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        fail_silently=False
                    )
                    
                    # Log notification
                    NotificationLog.objects.create(
                        recipient=recipient,
                        notification_type='business_alert',
                        method='email',
                        status='sent' if result else 'failed',
                        subject=subject,
                        message=text_message,
                        metadata={
                            'alert_type': alert_type,
                            'alert_data': alert_data
                        }
                    )
                    
                    if result:
                        success_count += 1
                        logger.info(f"Business alert sent to {recipient.email} for {alert_type}")
                    else:
                        logger.error(f"Failed to send business alert to {recipient.email}")
                        
                except Exception as recipient_error:
                    logger.error(f"Error sending business alert to {recipient.email}: {str(recipient_error)}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to send business alert {alert_type}: {str(e)}")
            return False
    
    @staticmethod
    def _generate_business_alert_content(alert_type, alert_data):
        """Generate email content for business alerts"""
        
        alert_configs = {
            'booking_timeout': {
                'subject': '⚠️ Booking Timeout Alert',
                'title': 'Booking Timeout Detected',
                'description': 'Some bookings have exceeded their expected completion time.',
                'color': '#ff6b6b'
            },
            'pending_signature': {
                'subject': '📝 Pending Signature Alert',
                'title': 'Signatures Pending',
                'description': 'Multiple bookings are waiting for customer signatures.',
                'color': '#ffa726'
            },
            'payment_hold': {
                'subject': '💳 Payment Hold Alert',
                'title': 'Payments on Hold',
                'description': 'Some payments are stuck in escrow and need attention.',
                'color': '#ef5350'
            },
            'low_vendor_count': {
                'subject': '👥 Low Vendor Count Alert',
                'title': 'Vendor Shortage',
                'description': 'Some areas have insufficient vendor coverage.',
                'color': '#ff9800'
            },
        }
        
        config = alert_configs.get(alert_type, {
            'subject': '🚨 System Alert',
            'title': 'System Alert',
            'description': 'System attention required.',
            'color': '#f44336'
        })
        
        subject = config['subject']
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: {config['color']}; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">{config['title']}</h1>
            </div>
            <div style="padding: 30px; background-color: #f8f9fa;">
                <h2 style="color: #333;">Action Required</h2>
                <p>{config['description']}</p>
                
                <div style="background: #fff; border: 1px solid #dee2e6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #495057;">Alert Details:</h3>
                    <ul style="color: #6c757d;">
        """
        
        # Add alert-specific details
        for key, value in alert_data.items():
            if key != 'items':  # Handle items separately
                html_message += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        
        html_message += "</ul>"
        
        # Add items if present
        if 'items' in alert_data and alert_data['items']:
            html_message += "<h4>Affected Items:</h4><ul>"
            for item in alert_data['items'][:10]:  # Limit to 10 items
                html_message += f"<li>{item}</li>"
            if len(alert_data['items']) > 10:
                html_message += f"<li>... and {len(alert_data['items']) - 10} more</li>"
            html_message += "</ul>"
        
        html_message += f"""
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #dc3545; font-weight: bold;">Please review and take appropriate action.</p>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #999; font-size: 12px;">
                    This is an automated alert from HomeServe Pro monitoring system.
                    Generated at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
                </p>
            </div>
        </body>
        </html>
        """
        
        text_message = f"""
        {config['title']}
        
        {config['description']}
        
        Alert Details:
        """
        
        for key, value in alert_data.items():
            if key != 'items':
                text_message += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        if 'items' in alert_data and alert_data['items']:
            text_message += f"\nAffected Items ({len(alert_data['items'])}):\n"
            for item in alert_data['items'][:5]:  # Limit to 5 for text
                text_message += f"- {item}\n"
            if len(alert_data['items']) > 5:
                text_message += f"... and {len(alert_data['items']) - 5} more\n"
        
        text_message += f"""
        
        Please review and take appropriate action.
        
        Generated at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        
        ---
        HomeServe Pro Monitoring System
        """
        
        return subject, html_message, text_message


# Backward compatibility
class OTPService:
    """Legacy OTP service for backward compatibility"""
    
    @staticmethod
    def generate_otp(length=6):
        return NotificationService.generate_otp(length)
    
    @staticmethod
    def send_otp_sms(phone_number, otp):
        return NotificationService.send_otp_sms(phone_number, otp)
    
    @staticmethod
    def store_otp(phone_number, otp, ttl=300):
        return NotificationService.store_otp(phone_number, otp, ttl)
    
    @staticmethod
    def verify_otp(phone_number, otp):
        return NotificationService.verify_otp(phone_number, otp)
    
    @staticmethod
    def send_and_store_otp(phone_number):
        result = NotificationService.send_and_store_otp(phone_number, method='sms')
        return {
            'otp_sent': result.get('otp_sent', False),
            'otp': result.get('otp')
        }