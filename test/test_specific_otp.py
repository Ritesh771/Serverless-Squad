#!/usr/bin/env python3
"""
Quick test for the specific OTP issue with riturithesh66@gmail.com
"""

import requests
import json

def test_otp_for_user():
    """Test OTP functionality for the specific user email"""
    
    print("🧪 Testing OTP for riturithesh66@gmail.com\n")
    
    BASE_URL = "http://localhost:8000"
    
    # Test OTP sending with user creation
    print("1. Testing Send OTP with User Creation...")
    otp_data = {
        "email": "riturithesh66@gmail.com",
        "method": "email",
        "create_user": True,
        "username": "riturithesh66"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/send-otp/", json=otp_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS! OTP sent successfully")
            print(f"   Message: {data.get('message')}")
            if 'otp' in data:
                otp_code = data['otp']
                print(f"   🔑 OTP Code: {otp_code}")
                
                # Now test OTP verification
                print(f"\n2. Testing OTP Verification...")
                verify_data = {
                    "email": "riturithesh66@gmail.com",
                    "otp": otp_code
                }
                
                verify_response = requests.post(f"{BASE_URL}/auth/verify-otp/", json=verify_data)
                print(f"   Status: {verify_response.status_code}")
                
                if verify_response.status_code == 200:
                    verify_result = verify_response.json()
                    print("   ✅ SUCCESS! OTP verified successfully")
                    print(f"   User created: {verify_result.get('user', {}).get('username')}")
                    print(f"   Access token received: {'access' in verify_result}")
                else:
                    print("   ❌ OTP verification failed")
                    print(f"   Error: {verify_response.text}")
            else:
                print("   ℹ️  OTP sent but not returned (production mode)")
                print("   Check email for OTP code to test verification")
        else:
            print("   ❌ Failed to send OTP")
            print(f"   Error: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    print(f"\n📝 Summary:")
    print("   - If this works, the Redis bypass is successful")
    print("   - The authentication system should now work in your frontend")
    print("   - You can use the frontend registration with OTP verification")

if __name__ == "__main__":
    test_otp_for_user()