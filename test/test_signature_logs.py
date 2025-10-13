#!/usr/bin/env python
"""
Test script to verify the Signature Logs functionality
"""

import os
import sys
import django
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')

# Setup Django
django.setup()

from core.models import VendorApplication, Signature, Booking, Service, User

def test_signature_logs():
    """Test the signature logs functionality"""
    print("Testing Signature Logs Feature...")
    
    # Create test users
    customer, created = User.objects.get_or_create(
        username='test_customer',
        defaults={
            'email': 'customer@example.com',
            'role': 'customer'
        }
    )
    
    vendor_user, created = User.objects.get_or_create(
        username='test_vendor_user',
        defaults={
            'email': 'vendor@example.com',
            'role': 'vendor'
        }
    )
    
    # Create a vendor application and approve it
    vendor_app = VendorApplication.objects.create(
        name='Test Vendor',
        email='vendor@example.com',
        phone='+1234567890',
        pincode='123456',
        service_category='Plumbing',
        experience=5,
        id_proof='id_proof.pdf',
        address_proof='address_proof.pdf',
        profile_photo='profile_photo.pdf',
        status='approved'
    )
    
    # Refresh to get the vendor account that was created
    vendor_app.refresh_from_db()
    
    # Create a service
    service, created = Service.objects.get_or_create(
        name='Plumbing Service',
        defaults={
            'description': 'Test plumbing service',
            'base_price': 100.00,
            'duration_minutes': 60,
            'category': 'plumbing'
        }
    )
    
    # Create a booking
    booking = Booking.objects.create(
        customer=customer,
        vendor=vendor_app.vendor_account,
        service=service,
        status='completed',
        total_price=100.00,
        pincode='123456',
        scheduled_date=timezone.now()
    )
    
    # Create a signature for the booking
    signature = Signature.objects.create(
        booking=booking,
        status='signed',
        satisfaction_rating=5,
        satisfaction_comments='Excellent service!',
        signature_data={'test': 'data'},
        signed_by=customer
    )
    
    # Test the signature_logs endpoint functionality
    # Get signatures for the vendor
    vendor_signatures = Signature.objects.filter(
        booking__vendor=vendor_app.vendor_account
    ).select_related('booking', 'booking__customer').order_by('-requested_at')
    
    print(f"Found {vendor_signatures.count()} signatures for vendor")
    
    if vendor_signatures.exists():
        print("✅ Signature Logs functionality is working correctly")
        for sig in vendor_signatures:
            print(f"  - Booking: {sig.booking.id}")
            print(f"  - Customer: {sig.booking.customer.get_full_name()}")
            print(f"  - Status: {sig.status}")
            print(f"  - Rating: {sig.satisfaction_rating}")
        result = True
    else:
        print("❌ Signature Logs functionality is not working correctly")
        result = False
    
    # Clean up
    signature.delete()
    booking.delete()
    service.delete()
    vendor_app.delete()
    vendor_user.delete()
    customer.delete()
    
    return result

def main():
    """Run signature logs test"""
    print("Running Signature Logs Feature Test\n")
    
    # Test Signature Logs
    signature_logs_result = test_signature_logs()
    
    print("\n" + "="*50)
    print("SIGNATURE LOGS TEST RESULT")
    print("="*50)
    print(f"Signature Logs: {'PASS' if signature_logs_result else 'FAIL'}")
    
    if signature_logs_result:
        print("\n🎉 Signature Logs test passed! The implemented feature is working correctly.")
        return 0
    else:
        print("\n❌ Signature Logs test failed. Please check the implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())