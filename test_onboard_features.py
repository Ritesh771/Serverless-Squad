#!/usr/bin/env python
"""
Test script to verify the Onboard Manager workflow features
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')

# Setup Django
django.setup()

from core.models import VendorApplication, AuditLog
from core.vendor_ai_service import VendorPerformanceAI

def test_ai_flagging():
    """Test the AI flagging functionality"""
    print("Testing AI Flagging System...")
    
    # Create a test vendor application with suspicious data
    User = get_user_model()
    test_user, created = User.objects.get_or_create(
        username='test_vendor',
        defaults={
            'email': 'test@example.com',
            'role': 'vendor'
        }
    )
    
    # Create an application that should be flagged
    suspicious_app = VendorApplication.objects.create(
        name='A',  # Very short name
        email='invalid-email',  # Invalid email
        phone='123',  # Invalid phone
        pincode='123456',
        service_category='Plumbing',
        experience=5,
        id_proof='id_proof.pdf',
        address_proof='address_proof.pdf',
        profile_photo='profile_photo.pdf'
    )
    
    # Analyze the application
    analysis_result = VendorPerformanceAI.analyze_vendor_application(suspicious_app)
    
    print(f"Analysis Result: {analysis_result}")
    
    # Check if the application was flagged
    if analysis_result['should_flag']:
        print("✅ AI Flagging is working correctly - application was flagged")
        print(f"Flag reasons: {analysis_result['flag_reasons']}")
    else:
        print("❌ AI Flagging is not working correctly - application was not flagged")
    
    # Clean up
    suspicious_app.delete()
    test_user.delete()
    
    return analysis_result['should_flag']

def test_audit_logging():
    """Test the audit logging functionality"""
    print("\nTesting Audit Logging...")
    
    # Create a test vendor application
    User = get_user_model()
    test_user, created = User.objects.get_or_create(
        username='test_vendor2',
        defaults={
            'email': 'test2@example.com',
            'role': 'vendor'
        }
    )
    
    # Create a test onboard manager
    onboard_manager, created = User.objects.get_or_create(
        username='onboard_manager',
        defaults={
            'email': 'manager@example.com',
            'role': 'onboard_manager'
        }
    )
    
    # Create an application
    app = VendorApplication.objects.create(
        name='Test Vendor',
        email='test2@example.com',
        phone='+1234567890',
        pincode='123456',
        service_category='Plumbing',
        experience=5,
        id_proof='id_proof.pdf',
        address_proof='address_proof.pdf',
        profile_photo='profile_photo.pdf'
    )
    
    # Log an edit action
    from core.utils import AuditLogger
    AuditLogger.log_action(
        user=onboard_manager,
        action='update',
        resource_type='VendorApplication',
        resource_id=str(app.id),
        old_values={'name': 'Old Name'},
        new_values={'name': 'New Name'}
    )
    
    # Check if the audit log was created
    audit_logs = AuditLog.objects.filter(
        resource_type='VendorApplication',
        resource_id=str(app.id)
    )
    
    result = audit_logs.exists()
    
    if result:
        print("✅ Audit Logging is working correctly")
        for log in audit_logs:
            print(f"  - Action: {log.action}, User: {log.user.username}")
    else:
        print("❌ Audit Logging is not working correctly")
    
    # Clean up
    app.delete()
    test_user.delete()
    onboard_manager.delete()
    audit_logs.delete()
    
    return result

def main():
    """Run all tests"""
    print("Running Onboard Manager Workflow Feature Tests\n")
    
    # Test AI Flagging
    ai_flag_result = test_ai_flagging()
    
    # Test Audit Logging
    audit_log_result = test_audit_logging()
    
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    print(f"AI Flagging: {'PASS' if ai_flag_result else 'FAIL'}")
    print(f"Audit Logging: {'PASS' if audit_log_result else 'FAIL'}")
    
    if ai_flag_result and audit_log_result:
        print("\n🎉 All tests passed! The implemented features are working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())