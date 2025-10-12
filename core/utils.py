import random
import string
from django.core.cache import cache
from django.conf import settings
from .notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


class OTPService:
    """Service for OTP generation and verification"""
    
    @staticmethod
    def generate_otp(length=6):
        """Generate a random OTP"""
        return NotificationService.generate_otp(length)
    
    @staticmethod
    def send_otp_sms(phone_number, otp):
        """Send OTP via SMS - Now disabled, use email instead"""
        return NotificationService.send_otp_sms(phone_number, otp)
    
    @staticmethod
    def send_otp_email(email, otp, user_name=""):
        """Send OTP via email"""
        return NotificationService.send_otp_email(email, otp, user_name)
    
    @staticmethod
    def store_otp(identifier, otp, ttl=300):  # 5 minutes TTL
        """Store OTP in cache with TTL"""
        return NotificationService.store_otp(identifier, otp, ttl)
    
    @staticmethod
    def verify_otp(identifier, otp):
        """Verify OTP against cached value"""
        return NotificationService.verify_otp(identifier, otp)
    
    @staticmethod
    def send_and_store_otp(identifier, method='email', user_name=""):
        """Generate, send, and store OTP - now defaults to email"""
        return NotificationService.send_and_store_otp(identifier, method, user_name)


class AuditLogger:
    """Service for logging user actions"""
    
    @staticmethod
    def log_action(user, action, resource_type, resource_id, old_values=None, new_values=None, request=None):
        """Log user action to audit trail"""
        from .models import AuditLog
        
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = AuditLogger.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
        
        AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip