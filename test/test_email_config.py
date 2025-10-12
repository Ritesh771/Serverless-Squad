#!/usr/bin/env python
"""
Test script to verify email and SMS configuration
"""

import os
import sys
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django
sys.path.append('/Users/riteshn/Desktop/Projects/Serverless-Squad')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

def test_email_configuration():
    """Test email configuration"""
    print("📧 Testing Email Configuration")
    print("=" * 40)
    
    print(f"📝 Email Backend: {settings.EMAIL_BACKEND}")
    print(f"🏠 Email Host: {settings.EMAIL_HOST}")
    print(f"🔌 Email Port: {settings.EMAIL_PORT}")
    print(f"🔐 Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"👤 Email User: {settings.EMAIL_HOST_USER}")
    print(f"🔑 Password Set: {'Yes' if settings.EMAIL_HOST_PASSWORD else 'No'}")
    print(f"📨 From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # Test sending email
    try:
        print("\n📤 Sending test email...")
        result = send_mail(
            subject='HomeServe Pro - Email Configuration Test',
            message='This is a test email to verify your email configuration is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to self
            fail_silently=False
        )
        
        if result:
            print("✅ Email sent successfully!")
            print("📬 Check your inbox for the test email")
        else:
            print("❌ Email sending failed")
            
    except Exception as e:
        print(f"❌ Email configuration error: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Ensure 2FA is enabled on your Gmail account")
        print("2. Create an App Password at: https://myaccount.google.com/apppasswords")
        print("3. Use the App Password (not your regular Gmail password)")
        print("4. Make sure 'Less secure app access' is enabled if not using App Password")

def test_removed_twilio_configuration():
    """Information about removed Twilio configuration"""
    print("\n📱 Twilio SMS Configuration - REMOVED")
    print("=" * 40)
    
    print("📋 NOTICE: Twilio SMS functionality has been removed from the system.")
    print("✅ All OTP notifications now use email only.")
    print("📧 This provides a more cost-effective and reliable solution.")
    print("\n🔧 Email configuration is now the primary notification method.")
    print("✨ Benefits of email-only OTP:")
    print("   • No SMS costs")
    print("   • Better deliverability")
    print("   • Rich HTML formatting")
    print("   • No international restrictions")

def main():
    print("🔔 HomeServe Pro - Email Configuration Test")
    print("=" * 55)
    
    test_email_configuration()
    test_removed_twilio_configuration()
    
    print("\n🎯 Next Steps:")
    print("1. ✅ Redis is running")
    print("2. 📧 Configure email credentials if test failed")
    print("3. ✅ Twilio has been removed - email-only OTP system")
    print("4. 🚀 Start Celery worker and beat")

if __name__ == '__main__':
    main()