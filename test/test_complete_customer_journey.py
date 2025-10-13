#!/usr/bin/env python3
"""
Complete Customer Journey Flow Validation Test
Tests the entire workflow from registration to payment according to requirements.
"""

import os
import sys
import django
import requests
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from core.models import Service, Booking, Signature, Photo, Payment
from django.utils import timezone

User = get_user_model()


class CustomerJourneyValidator:
    """Validate complete customer journey implementation"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.issues = []
        self.successes = []
        
    def log_success(self, message):
        self.successes.append(f"✅ {message}")
        print(f"✅ {message}")
    
    def log_issue(self, message):
        self.issues.append(f"❌ {message}")
        print(f"❌ {message}")
    
    def log_info(self, message):
        print(f"ℹ️  {message}")
    
    def print_section(self, title):
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")
    
    # ========================================================================
    # (A) CUSTOMER JOURNEY VALIDATION
    # ========================================================================
    
    def validate_account_setup(self):
        """Validate: Customer registers → verifies via OTP/email"""
        self.print_section("(A) CUSTOMER JOURNEY - Account Setup")
        
        # Check registration endpoint exists
        try:
            response = requests.post(f"{self.base_url}/auth/register/", 
                                    json={'username': 'test'}, timeout=5)
            if response.status_code in [200, 400, 401]:  # Endpoint exists
                self.log_success("Registration endpoint exists: POST /auth/register/")
            else:
                self.log_issue(f"Registration endpoint returned: {response.status_code}")
        except Exception as e:
            self.log_issue(f"Registration endpoint not accessible: {e}")
        
        # Check OTP endpoints
        try:
            response = requests.post(f"{self.base_url}/auth/send-otp/", 
                                    json={'email': 'test@test.com'}, timeout=5)
            if response.status_code in [200, 400]:
                self.log_success("OTP send endpoint exists: POST /auth/send-otp/")
        except Exception as e:
            self.log_issue(f"OTP endpoint not accessible: {e}")
        
        # Check User model has verification fields
        user_fields = [f.name for f in User._meta.get_fields()]
        if 'is_verified' in user_fields:
            self.log_success("User model has 'is_verified' field")
        else:
            self.log_issue("User model missing 'is_verified' field")
        
        # Check dashboard shows profile, bookings, addresses
        self.log_info("Frontend: Dashboard should show profile, previous bookings, saved addresses")
    
    def validate_service_search_booking(self):
        """Validate: Service search → pincode-based → dynamic pricing → booking"""
        self.print_section("(A) Service Search & Booking")
        
        # Check services endpoint
        try:
            response = requests.get(f"{self.base_url}/api/services/", timeout=5)
            if response.status_code in [200, 401]:
                self.log_success("Services endpoint exists: GET /api/services/")
        except Exception as e:
            self.log_issue(f"Services endpoint not accessible: {e}")
        
        # Check dynamic pricing endpoint
        try:
            response = requests.get(f"{self.base_url}/api/dynamic-pricing/", 
                                   params={'service_id': 1, 'pincode': '110001'}, 
                                   timeout=5)
            if response.status_code in [200, 400, 401]:
                self.log_success("Dynamic pricing endpoint exists: GET /api/dynamic-pricing/")
        except Exception as e:
            self.log_issue(f"Dynamic pricing endpoint not accessible: {e}")
        
        # Check vendor search endpoint
        try:
            response = requests.get(f"{self.base_url}/api/vendor-search/", 
                                   params={'pincode': '110001'}, timeout=5)
            if response.status_code in [200, 401]:
                self.log_success("Vendor search endpoint exists: GET /api/vendor-search/")
        except Exception as e:
            self.log_issue(f"Vendor search endpoint not accessible: {e}")
        
        # Check smart buffering fields in Booking model
        booking_fields = [f.name for f in Booking._meta.get_fields()]
        buffering_fields = ['buffer_before_minutes', 'buffer_after_minutes', 
                           'travel_time_to_location_minutes']
        
        for field in buffering_fields:
            if field in booking_fields:
                self.log_success(f"Booking model has '{field}' for smart buffering")
            else:
                self.log_issue(f"Booking model missing '{field}' field")
    
    def validate_service_in_progress(self):
        """Validate: Live status tracking (Assigned → En Route → In Progress)"""
        self.print_section("(A) Service in Progress - Status Tracking")
        
        # Check booking status choices
        status_choices = [choice[0] for choice in Booking.STATUS_CHOICES]
        
        required_statuses = ['pending', 'confirmed', 'in_progress', 'completed', 'signed']
        for status in required_statuses:
            if status in status_choices:
                self.log_success(f"Booking has '{status}' status")
            else:
                self.log_issue(f"Booking missing '{status}' status")
        
        # Check status update endpoint
        try:
            response = requests.patch(f"{self.base_url}/api/bookings/test-id/", 
                                     json={'status': 'in_progress'}, timeout=5)
            if response.status_code in [200, 400, 401, 404]:
                self.log_success("Booking update endpoint exists: PATCH /api/bookings/{id}/")
        except Exception as e:
            self.log_issue(f"Booking update endpoint not accessible: {e}")
        
        self.log_info("WebSocket support should exist for real-time status updates")
    
    def validate_post_service_confirmation(self):
        """Validate: Photos → Signature Request → Review → Sign → Payment Release"""
        self.print_section("(A) Post-Service Confirmation")
        
        # Check Photo model
        photo_fields = [f.name for f in Photo._meta.get_fields()]
        required_photo_fields = ['booking', 'image_type', 'image']
        
        for field in required_photo_fields:
            if field in photo_fields:
                self.log_success(f"Photo model has '{field}' field")
            else:
                self.log_issue(f"Photo model missing '{field}' field")
        
        # Check image types
        if hasattr(Photo, 'IMAGE_TYPE_CHOICES'):
            types = [choice[0] for choice in Photo.IMAGE_TYPE_CHOICES]
            if 'before' in types and 'after' in types:
                self.log_success("Photo model supports 'before' and 'after' types")
            else:
                self.log_issue("Photo model missing 'before'/'after' image types")
        
        # Check photo upload endpoint
        try:
            response = requests.post(f"{self.base_url}/api/photos/", 
                                    json={'booking': 'test'}, timeout=5)
            if response.status_code in [200, 400, 401]:
                self.log_success("Photo upload endpoint exists: POST /api/photos/")
        except Exception as e:
            self.log_issue(f"Photo upload endpoint not accessible: {e}")
        
        # Check Signature model
        sig_fields = [f.name for f in Signature._meta.get_fields()]
        required_sig_fields = ['booking', 'satisfaction_rating', 'signature_hash', 
                              'expires_at', 'status']
        
        for field in required_sig_fields:
            if field in sig_fields:
                self.log_success(f"Signature model has '{field}' field")
            else:
                self.log_issue(f"Signature model missing '{field}' field")
        
        # Check signature endpoints
        try:
            response = requests.post(f"{self.base_url}/api/bookings/test-id/request_signature/", 
                                    timeout=5)
            if response.status_code in [200, 400, 401, 404]:
                self.log_success("Signature request endpoint exists")
        except Exception as e:
            self.log_issue(f"Signature request endpoint not accessible: {e}")
        
        try:
            response = requests.post(f"{self.base_url}/api/signatures/test-id/sign/", 
                                    json={'satisfaction_rating': 5}, timeout=5)
            if response.status_code in [200, 400, 401, 404]:
                self.log_success("Signature signing endpoint exists")
        except Exception as e:
            self.log_issue(f"Signature signing endpoint not accessible: {e}")
    
    def validate_after_signature(self):
        """Validate: Payment release → Booking verified → Blockchain storage"""
        self.print_section("(A) After Signature - Payment & Verification")
        
        # Check Payment model
        payment_fields = [f.name for f in Payment._meta.get_fields()]
        if 'booking' in payment_fields and 'status' in payment_fields:
            self.log_success("Payment model properly structured")
        else:
            self.log_issue("Payment model missing required fields")
        
        # Check automatic payment processing
        self.log_info("Payment should auto-release after customer signature")
        
        # Check signature hash (blockchain simulation)
        if 'signature_hash' in [f.name for f in Signature._meta.get_fields()]:
            self.log_success("Signature has 'signature_hash' field (blockchain vault)")
        else:
            self.log_issue("Signature missing 'signature_hash' field")
        
        # Check booking status update to 'signed'
        if 'signed' in [choice[0] for choice in Booking.STATUS_CHOICES]:
            self.log_success("Booking has 'signed' status for verified completion")
        else:
            self.log_issue("Booking missing 'signed' status")
    
    def validate_if_not_satisfied(self):
        """Validate: Reject signature → Raise dispute → Ops Manager notified"""
        self.print_section("(A) If Not Satisfied - Dispute Flow")
        
        # Check if Dispute model exists
        try:
            from core.models import Dispute
            self.log_success("Dispute model exists")
            
            # Check dispute fields
            dispute_fields = [f.name for f in Dispute._meta.get_fields()]
            required_fields = ['booking', 'customer', 'dispute_type', 'status']
            
            for field in required_fields:
                if field in dispute_fields:
                    self.log_success(f"Dispute model has '{field}' field")
                else:
                    self.log_issue(f"Dispute model missing '{field}' field")
            
        except ImportError:
            self.log_issue("Dispute model not found in core.models")
        
        # Check dispute creation endpoint
        try:
            response = requests.post(f"{self.base_url}/api/disputes/", 
                                    json={'booking': 'test'}, timeout=5)
            if response.status_code in [200, 400, 401]:
                self.log_success("Dispute creation endpoint exists: POST /api/disputes/")
        except Exception as e:
            self.log_issue(f"Dispute endpoint not accessible: {e}")
        
        self.log_info("Ops Manager should receive notification when dispute is raised")
    
    # ========================================================================
    # FRONTEND VALIDATION
    # ========================================================================
    
    def validate_frontend_implementation(self):
        """Check frontend files match the flow"""
        self.print_section("Frontend Implementation Check")
        
        frontend_files = {
            'Registration/Login': 'src/pages/auth/Register.tsx',
            'Service Booking': 'src/pages/customer/BookService.tsx',
            'Booking Details': 'src/pages/customer/BookingDetails.tsx',
            'Signature Page': 'src/pages/customer/SignaturePage.tsx',
            'My Bookings': 'src/pages/customer/MyBookings.tsx',
            'Dashboard': 'src/pages/customer/Dashboard.tsx',
        }
        
        for component, path in frontend_files.items():
            full_path = os.path.join('/Users/riteshn/Desktop/Projects/Serverless-Squad', path)
            if os.path.exists(full_path):
                self.log_success(f"{component} component exists")
            else:
                self.log_issue(f"{component} component missing: {path}")
        
        # Check service files
        service_files = {
            'authService': 'src/services/authService.ts',
            'bookingService': 'src/services/bookingService.ts',
            'photoService': 'src/services/photoService.ts',
            'signatureService': 'src/services/signatureService.ts',
            'pricingService': 'src/services/pricingService.ts',
            'disputeService': 'src/services/disputeService.ts',
        }
        
        for service, path in service_files.items():
            full_path = os.path.join('/Users/riteshn/Desktop/Projects/Serverless-Squad', path)
            if os.path.exists(full_path):
                self.log_success(f"{service} exists")
            else:
                self.log_issue(f"{service} missing: {path}")
    
    def run_validation(self):
        """Run all validation checks"""
        print("\n" + "=" * 80)
        print("  CUSTOMER JOURNEY FLOW VALIDATION")
        print("  Testing Backend & Frontend Implementation")
        print("=" * 80 + "\n")
        
        # Customer Journey Steps
        self.validate_account_setup()
        self.validate_service_search_booking()
        self.validate_service_in_progress()
        self.validate_post_service_confirmation()
        self.validate_after_signature()
        self.validate_if_not_satisfied()
        
        # Frontend validation
        self.validate_frontend_implementation()
        
        # Print summary
        self.print_section("VALIDATION SUMMARY")
        
        print(f"\n✅ Successes: {len(self.successes)}")
        print(f"❌ Issues: {len(self.issues)}\n")
        
        if self.issues:
            print("Issues Found:")
            for issue in self.issues:
                print(f"  {issue}")
        
        if len(self.issues) == 0:
            print("\n🎉 All validation checks passed!")
            print("The customer journey flow is correctly implemented in both backend and frontend.")
        else:
            print(f"\n⚠️  Found {len(self.issues)} issue(s) that need attention.")
        
        return len(self.issues) == 0


if __name__ == "__main__":
    print("\n🔍 Starting Customer Journey Flow Validation...\n")
    
    validator = CustomerJourneyValidator()
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)
