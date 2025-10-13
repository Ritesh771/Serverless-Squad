#!/usr/bin/env python3
"""
Test script to verify authentication endpoints are working correctly.
This helps debug the authentication issues seen in the server logs.
"""

import requests
import json

# Base URL for the Django backend
BASE_URL = "http://localhost:8000"

def test_auth_endpoints():
    """Test various authentication endpoints"""
    
    print("🔧 Testing HomeServe Pro Authentication Endpoints\n")
    
    # 1. Test login endpoint
    print("1. Testing Login Endpoint...")
    login_data = {
        "username": "admin",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print("   ❌ Login failed")
            print(f"   Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    print()
    
    # 2. Test OTP sending
    print("2. Testing Send OTP Endpoint...")
    otp_data = {
        "email": "test@example.com",
        "method": "email",
        "create_user": True,
        "username": "testuser"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/send-otp/", json=otp_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Send OTP endpoint working")
            data = response.json()
            print(f"   Message: {data.get('message')}")
            if 'otp' in data:
                print(f"   DEBUG OTP: {data['otp']}")
        else:
            print("   ❌ Send OTP failed")
            print(f"   Error: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    print()
    
    # 3. Test endpoint existence
    print("3. Testing Endpoint Availability...")
    endpoints_to_test = [
        "/auth/login/",
        "/auth/refresh/", 
        "/auth/send-otp/",
        "/auth/verify-otp/",
        "/auth/vendor/send-otp/",
        "/auth/vendor/verify-otp/",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            # Use HEAD request to check if endpoint exists
            response = requests.head(f"{BASE_URL}{endpoint}")
            if response.status_code != 404:
                print(f"   ✅ {endpoint} - Available")
            else:
                print(f"   ❌ {endpoint} - Not Found")
        except requests.exceptions.RequestException:
            print(f"   ❌ {endpoint} - Connection Error")
    
    print("\n📊 Summary:")
    print("   - If login shows 401, check user credentials in Django admin")
    print("   - If endpoints show 404, check Django URL configuration")
    print("   - If connection errors, ensure Django server is running on port 8000")

if __name__ == "__main__":
    test_auth_endpoints()