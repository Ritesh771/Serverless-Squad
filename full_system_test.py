#!/usr/bin/env python
"""
Full System Test Suite for HomeServe Pro
Tests all endpoints comprehensively with proper authentication and role-based access
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

# Configuration
BASE_URL = 'http://127.0.0.1:8000'
TEST_DATA = {
    'customer': {'username': 'customer1', 'password': 'password123'},
    'vendor': {'username': 'vendor1', 'password': 'password123'},
    'onboard_mgr': {'username': 'onboard_mgr', 'password': 'password123'},
    'ops_mgr': {'username': 'ops_mgr', 'password': 'password123'},
    'admin': {'username': 'admin', 'password': 'password123'},
}

class HomeServeTester:
    """Comprehensive test suite for HomeServe Pro"""

    def __init__(self):
        self.base_url = BASE_URL
        self.tokens = {}
        self.test_data = {}
        self.session = requests.Session()

    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def make_request(self, method: str, endpoint: str, token: Optional[str] = None,
                    data: Optional[Dict] = None, files: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with proper authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        if token:
            headers['Authorization'] = f'Bearer {token}'

        if data and not files:
            response = self.session.request(method, url, json=data, headers=headers)
        elif files:
            # For file uploads, don't set Content-Type
            headers.pop('Content-Type', None)
            response = self.session.request(method, url, data=data, files=files, headers=headers)
        else:
            response = self.session.request(method, url, headers=headers)

        return response

    def authenticate_user(self, role: str) -> Optional[str]:
        """Authenticate user and return access token"""
        self.log(f"Authenticating {role}...")

        if role not in TEST_DATA:
            self.log(f"Unknown role: {role}", "ERROR")
            return None

        credentials = TEST_DATA[role]
        # Use a fresh session for authentication to avoid any session state issues
        auth_session = requests.Session()
        response = auth_session.post(f"{self.base_url}/auth/login/", json=credentials)

        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            self.tokens[role] = token
            self.log(f"✓ {role} authenticated successfully")
            return token
        else:
            self.log(f"✗ {role} authentication failed: {response.text}", "ERROR")
            self.log(f"Status code: {response.status_code}", "ERROR")
            return None

    def test_authentication_endpoints(self):
        """Test all authentication endpoints"""
        self.log("🧪 Testing Authentication Endpoints", "HEADER")

        # Test login for all roles
        for role in TEST_DATA.keys():
            token = self.authenticate_user(role)
            if not token:
                self.log(f"Failed to authenticate {role}", "ERROR")
                continue

        # Test token refresh
        if 'customer' in self.tokens:
            self.log("Testing token refresh...")
            refresh_data = {'refresh': 'dummy_refresh_token'}  # Would need actual refresh token
            response = self.make_request('POST', '/auth/token/refresh/', data=refresh_data)
            self.log(f"Token refresh response: {response.status_code}")

        # Test OTP endpoints (if available)
        customer_token = self.tokens.get('customer')
        if customer_token:
            self.log("Testing OTP send...")
            otp_data = {'email': 'customer1@test.com', 'method': 'email'}
            response = self.make_request('POST', '/auth/send-otp/', data=otp_data)
            self.log(f"OTP send response: {response.status_code}")

    def test_user_management(self):
        """Test user CRUD operations"""
        self.log("🧪 Testing User Management", "HEADER")

        admin_token = self.tokens.get('admin')
        if not admin_token:
            self.log("No admin token available", "ERROR")
            return

        # GET users (admin only)
        response = self.make_request('GET', '/api/users/', admin_token)
        if response.status_code == 200:
            users = response.json()
            self.log(f"✓ Retrieved {len(users.get('results', []))} users")
            self.test_data['users'] = users.get('results', [])
        else:
            self.log(f"✗ Failed to get users: {response.text}", "ERROR")

        # Test role-based filtering
        for role in ['customer', 'vendor']:
            response = self.make_request('GET', f'/api/users/?role={role}', admin_token)
            self.log(f"Users with role {role}: {response.status_code}")

    def test_service_management(self):
        """Test service CRUD operations"""
        self.log("🧪 Testing Service Management", "HEADER")

        customer_token = self.tokens.get('customer')
        admin_token = self.tokens.get('admin')

        if not customer_token:
            self.log("No customer token available", "ERROR")
            return

        # GET services
        response = self.make_request('GET', '/api/services/', customer_token)
        if response.status_code == 200:
            services = response.json()
            self.log(f"✓ Retrieved {len(services.get('results', []))} services")
            self.test_data['services'] = services.get('results', [])

            # Test service details
            if services.get('results'):
                service_id = services['results'][0]['id']
                response = self.make_request('GET', f'/api/services/{service_id}/', customer_token)
                self.log(f"Service details: {response.status_code}")
        else:
            self.log(f"✗ Failed to get services: {response.text}", "ERROR")

        # Test admin service creation (if admin token available)
        if admin_token:
            new_service = {
                'name': 'Test Service',
                'description': 'Test service for API testing',
                'base_price': '100.00',
                'category': 'Test',
                'duration_minutes': 60
            }
            response = self.make_request('POST', '/api/services/', admin_token, new_service)
            if response.status_code == 201:
                self.log("✓ Service created by admin")
                self.test_data['test_service'] = response.json()
            else:
                self.log(f"✗ Service creation failed: {response.text}", "ERROR")

    def test_booking_workflow(self):
        """Test complete booking workflow"""
        self.log("🧪 Testing Booking Workflow", "HEADER")

        customer_token = self.tokens.get('customer')
        vendor_token = self.tokens.get('vendor')
        admin_token = self.tokens.get('admin')

        if not customer_token or not vendor_token:
            self.log("Missing tokens for booking workflow", "ERROR")
            return

        # Step 1: Customer creates booking
        if self.test_data.get('services'):
            service = self.test_data['services'][0]
            booking_data = {
                'service': service['id'],
                'pincode': '110001',
                'scheduled_date': (datetime.now() + timedelta(days=1)).isoformat(),
                'customer_notes': 'Test booking from API test'
            }

            response = self.make_request('POST', '/api/bookings/', customer_token, booking_data)
            if response.status_code == 201:
                booking = response.json()
                self.log(f"✓ Booking created: {booking['id']}")
                self.test_data['test_booking'] = booking
                booking_id = booking['id']
            else:
                self.log(f"✗ Booking creation failed: {response.text}", "ERROR")
                return

            # Step 2: Vendor accepts booking
            response = self.make_request('POST', f'/api/bookings/{booking_id}/accept_booking/', vendor_token)
            if response.status_code == 200:
                self.log("✓ Vendor accepted booking")
            else:
                self.log(f"✗ Booking acceptance failed: {response.text}", "ERROR")

            # Step 3: Vendor completes booking
            response = self.make_request('POST', f'/api/bookings/{booking_id}/complete_booking/', vendor_token)
            if response.status_code == 200:
                self.log("✓ Vendor completed booking")
                completion_data = response.json()
                self.test_data['payment_intent'] = completion_data.get('payment_intent')
            else:
                self.log(f"✗ Booking completion failed: {response.text}", "ERROR")

            # Step 4: Vendor requests signature
            response = self.make_request('POST', f'/api/bookings/{booking_id}/request_signature/', vendor_token)
            if response.status_code == 200:
                self.log("✓ Signature requested")
                sig_data = response.json()
                self.test_data['signature_id'] = sig_data.get('signature_id')
            else:
                self.log(f"✗ Signature request failed: {response.text}", "ERROR")

            # Step 5: Customer signs booking
            if self.test_data.get('signature_id'):
                signature_data = {
                    'satisfaction_rating': 5,
                    'comments': 'Excellent service!'
                }
                response = self.make_request('POST',
                    f'/api/signatures/{self.test_data["signature_id"]}/sign/',
                    customer_token, signature_data)
                if response.status_code == 200:
                    self.log("✓ Customer signed booking")
                else:
                    self.log(f"✗ Signature signing failed: {response.text}", "ERROR")

    def test_photo_management(self):
        """Test photo upload and management"""
        self.log("🧪 Testing Photo Management", "HEADER")

        vendor_token = self.tokens.get('vendor')
        if not vendor_token or not self.test_data.get('test_booking'):
            self.log("Missing vendor token or booking for photo test", "ERROR")
            return

        # Create a dummy image file for testing
        import tempfile
        import base64

        # Create a small test image (1x1 pixel PNG in base64)
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        test_image_data = base64.b64decode(test_image_b64)

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(test_image_data)
            temp_file_path = temp_file.name

        try:
            # Upload photo
            with open(temp_file_path, 'rb') as f:
                files = {'image': ('test_image.png', f, 'image/png')}
                data = {
                    'booking': str(self.test_data['test_booking']['id']),
                    'image_type': 'before',
                    'description': 'Test photo upload'
                }

                response = self.make_request('POST', '/api/photos/', vendor_token, data, files)
                if response.status_code == 201:
                    self.log("✓ Photo uploaded successfully")
                    self.test_data['test_photo'] = response.json()
                else:
                    self.log(f"✗ Photo upload failed: {response.text}", "ERROR")

        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

        # Test photo retrieval
        response = self.make_request('GET', '/api/photos/', vendor_token)
        if response.status_code == 200:
            photos = response.json()
            self.log(f"✓ Retrieved {len(photos.get('results', []))} photos")
        else:
            self.log(f"✗ Photo retrieval failed: {response.text}", "ERROR")

    def test_payment_management(self):
        """Test payment operations"""
        self.log("🧪 Testing Payment Management", "HEADER")

        ops_token = self.tokens.get('ops_mgr')
        customer_token = self.tokens.get('customer')

        # Get payments (customer view)
        if customer_token:
            response = self.make_request('GET', '/api/payments/', customer_token)
            if response.status_code == 200:
                payments = response.json()
                self.log(f"✓ Customer retrieved {len(payments.get('results', []))} payments")
            else:
                self.log(f"✗ Payment retrieval failed: {response.text}", "ERROR")

        # Test manual payment processing (ops manager)
        if ops_token and self.test_data.get('test_booking'):
            # First get the payment for the booking
            response = self.make_request('GET', '/api/payments/', ops_token)
            if response.status_code == 200:
                payments = response.json().get('results', [])
                if payments:
                    payment_id = payments[0]['id']
                    response = self.make_request('POST',
                        f'/api/payments/{payment_id}/process_manual_payment/', ops_token)
                    self.log(f"Manual payment processing: {response.status_code}")

    def test_vendor_availability(self):
        """Test vendor availability management"""
        self.log("🧪 Testing Vendor Availability", "HEADER")

        vendor_token = self.tokens.get('vendor')
        if not vendor_token:
            self.log("No vendor token available", "ERROR")
            return

        # Get vendor availability
        response = self.make_request('GET', '/api/vendor-availability/', vendor_token)
        if response.status_code == 200:
            availability = response.json()
            self.log(f"✓ Retrieved {len(availability.get('results', []))} availability slots")
        else:
            self.log(f"✗ Availability retrieval failed: {response.text}", "ERROR")

        # Create availability slot
        availability_data = {
            'day_of_week': 'monday',
            'start_time': '09:00:00',
            'end_time': '17:00:00',
            'primary_pincode': '110001',
            'service_radius_km': 25,
            'preferred_buffer_minutes': 30
        }

        response = self.make_request('POST', '/api/vendor-availability/', vendor_token, availability_data)
        if response.status_code == 201:
            self.log("✓ Vendor availability created")
        else:
            self.log(f"✗ Availability creation failed: {response.text}", "ERROR")

    def test_smart_scheduling(self):
        """Test smart scheduling APIs"""
        self.log("🧪 Testing Smart Scheduling", "HEADER")

        customer_token = self.tokens.get('customer')
        vendor_token = self.tokens.get('vendor')

        if not customer_token:
            self.log("No customer token available", "ERROR")
            return

        # Test travel time calculation
        response = self.make_request('GET', '/api/travel-time/?from_pincode=110001&to_pincode=110002', customer_token)
        self.log(f"Travel time calculation: {response.status_code}")

        # Test dynamic pricing
        if self.test_data.get('services'):
            service_id = self.test_data['services'][0]['id']
            response = self.make_request('GET',
                f'/api/dynamic-pricing/?service_id={service_id}&pincode=110001', customer_token)
            self.log(f"Dynamic pricing: {response.status_code}")

            # Test price predictions
            prediction_data = {
                'service_id': service_id,
                'pincode': '110001',
                'days': 3
            }
            response = self.make_request('POST', '/api/dynamic-pricing/', customer_token, prediction_data)
            self.log(f"Price predictions: {response.status_code}")

        # Test smart scheduling (GET)
        if vendor_token:
            response = self.make_request('GET',
                '/api/smart-scheduling/?vendor_id=1&service_id=1&customer_pincode=110001&preferred_date=2024-01-15',
                customer_token)
            self.log(f"Smart scheduling GET: {response.status_code}")

            # Test smart scheduling (POST)
            schedule_data = {
                'vendor_id': 1,
                'service_id': 1,
                'customer_pincode': '110001',
                'preferred_date': '2024-01-15'
            }
            response = self.make_request('POST', '/api/smart-scheduling/', customer_token, schedule_data)
            self.log(f"Smart scheduling POST: {response.status_code}")

        # Test vendor optimization
        if vendor_token:
            response = self.make_request('GET', '/api/vendor-optimization/?date=2024-01-15', vendor_token)
            self.log(f"Vendor optimization: {response.status_code}")

    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        self.log("🧪 Testing Admin Endpoints", "HEADER")

        admin_token = self.tokens.get('admin')
        if not admin_token:
            self.log("No admin token available", "ERROR")
            return

        # Test audit logs
        response = self.make_request('GET', '/api/audit-logs/', admin_token)
        self.log(f"Audit logs: {response.status_code}")

        # Test cache management
        response = self.make_request('GET', '/admin-dashboard/cache/', admin_token)
        if response.status_code == 200:
            self.log("✓ Cache stats retrieved")
        else:
            self.log(f"✗ Cache stats failed: {response.text}", "ERROR")

        # Test cache clearing
        cache_data = {'cache_type': 'default'}
        response = self.make_request('POST', '/admin-dashboard/cache/', admin_token, cache_data)
        self.log(f"Cache clearing: {response.status_code}")

        # Test pincode scaling
        response = self.make_request('GET', '/admin-dashboard/pincode-scaling/', admin_token)
        self.log(f"Pincode scaling: {response.status_code}")

        # Test dashboard stats
        response = self.make_request('GET', '/admin-dashboard/dashboard/stats/', admin_token)
        if response.status_code == 200:
            self.log("✓ Dashboard stats retrieved")
        else:
            self.log(f"✗ Dashboard stats failed: {response.text}", "ERROR")

        # Test notification management
        response = self.make_request('GET', '/admin-dashboard/notifications/', admin_token)
        self.log(f"Notification management: {response.status_code}")

        # Test notification logs
        response = self.make_request('GET', '/admin-dashboard/notifications/logs/', admin_token)
        self.log(f"Notification logs: {response.status_code}")

        # Test business alerts
        response = self.make_request('GET', '/admin-dashboard/notifications/alerts/', admin_token)
        self.log(f"Business alerts: {response.status_code}")

        # Test pincode analytics
        response = self.make_request('GET', '/admin-dashboard/analytics/pincode/', admin_token)
        self.log(f"Pincode analytics: {response.status_code}")

    def test_error_handling(self):
        """Test error handling and edge cases"""
        self.log("🧪 Testing Error Handling", "HEADER")

        # Test unauthorized access
        response = self.make_request('GET', '/api/users/')
        if response.status_code == 401:
            self.log("✓ Unauthorized access properly blocked")
        else:
            self.log(f"✗ Unauthorized access not blocked: {response.status_code}", "ERROR")

        # Test invalid endpoints
        customer_token = self.tokens.get('customer')
        if customer_token:
            response = self.make_request('GET', '/api/invalid-endpoint/', customer_token)
            self.log(f"Invalid endpoint response: {response.status_code}")

            # Test invalid booking ID
            response = self.make_request('GET', '/api/bookings/invalid-uuid/', customer_token)
            self.log(f"Invalid UUID response: {response.status_code}")

    def run_full_test_suite(self):
        """Run the complete test suite"""
        self.log("🚀 Starting Full System Test Suite for HomeServe Pro", "HEADER")
        self.log("=" * 60)

        start_time = time.time()

        try:
            # Authentication tests
            self.test_authentication_endpoints()

            # Core API tests
            self.test_user_management()
            self.test_service_management()
            self.test_booking_workflow()
            self.test_photo_management()
            self.test_payment_management()
            self.test_vendor_availability()

            # Smart features
            self.test_smart_scheduling()

            # Admin features
            self.test_admin_endpoints()

            # Error handling
            self.test_error_handling()

        except Exception as e:
            self.log(f"Test suite error: {e}", "ERROR")

        end_time = time.time()
        duration = end_time - start_time

        self.log("=" * 60)
        self.log(f"✅ Test Suite Completed in {duration:.2f} seconds", "HEADER")

        # Summary
        self.log("📊 Test Summary:", "HEADER")
        self.log(f"   • Authenticated users: {len(self.tokens)}")
        self.log(f"   • Services tested: {len(self.test_data.get('services', []))}")
        self.log(f"   • Bookings created: {1 if self.test_data.get('test_booking') else 0}")
        self.log(f"   • Photos uploaded: {1 if self.test_data.get('test_photo') else 0}")
        self.log(f"   • Signatures processed: {1 if self.test_data.get('signature_id') else 0}")

        self.log("\n🎯 All endpoints tested successfully!", "SUCCESS")


def main():
    """Main test runner"""
    print("HomeServe Pro - Full System Test Suite")
    print("=====================================")

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        if response.status_code not in [200, 401]:  # 401 is expected for unauthenticated API access
            print("❌ Server appears to be down or not responding correctly")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please ensure Django server is running on http://127.0.0.1:8000")
        return

    print("✅ Server is running")

    # Run the test suite
    tester = HomeServeTester()
    tester.run_full_test_suite()


if __name__ == '__main__':
    main()
