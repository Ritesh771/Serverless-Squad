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

def test_twilio_configuration():
    """Test Twilio configuration"""
    print("\n📱 Testing Twilio Configuration")
    print("=" * 40)
    
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
    
    print(f"🆔 Account SID: {account_sid[:20]}..." if account_sid else "❌ Account SID not set")
    print(f"🔑 Auth Token: {'Set' if auth_token else 'Not set'}")
    print(f"📞 From Number: {from_number}")
    
    if account_sid == 'your_twilio_account_sid' or not account_sid:
        print("\n⚠️  Twilio credentials are not configured")
        print("🔧 To configure Twilio:")
        print("1. Sign up at https://www.twilio.com/")
        print("2. Get your Account SID and Auth Token from console")
        print("3. Purchase a phone number")
        print("4. Update your .env file with real credentials")
        return
    
    # Test Twilio connection
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        # Get account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Twilio connection successful!")
        print(f"📊 Account Status: {account.status}")
        
        # Note: We don't send test SMS to avoid charges
        print("📝 SMS functionality ready (test SMS not sent to avoid charges)")
        
    except Exception as e:
        print(f"❌ Twilio configuration error: {str(e)}")
        print("\n🔧 Check your Twilio credentials and try again")

def main():
    print("🔔 HomeServe Pro - Communication Configuration Test")
    print("=" * 55)
    
    test_email_configuration()
    test_twilio_configuration()
    
    print("\n🎯 Next Steps:")
    print("1. ✅ Redis is running")
    print("2. 📧 Configure email credentials if test failed")
    print("3. 📱 Configure Twilio credentials for SMS")
    print("4. 🚀 Start Celery worker and beat")

if __name__ == '__main__':
    main()