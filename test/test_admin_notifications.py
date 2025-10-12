#!/usr/bin/env python
"""
Test the admin notification endpoints to demonstrate the API functionality.
"""

import os
import sys
import requests
import json

def test_admin_endpoints():
    """Test the admin notification endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔔 Testing Admin Notification Endpoints")
    print("=" * 50)
    
    # Test endpoints (without authentication for demonstration)
    endpoints = [
        "/admin-dashboard/notifications/",
        "/admin-dashboard/notifications/logs/",
        "/admin-dashboard/notifications/alerts/",
        "/admin-dashboard/analytics/pincode/"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing: {endpoint}")
            
            # Test GET request
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {response.status_code}")
                print(f"📊 Data keys: {list(data.keys())}")
                
            elif response.status_code == 401:
                print(f"🔐 Authentication required: {response.status_code}")
                print("   This is expected - endpoints require admin authentication")
                
            elif response.status_code == 403:
                print(f"🚫 Forbidden: {response.status_code}")
                print("   This is expected - endpoints require admin role")
                
            else:
                print(f"ℹ️  Response: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - make sure Django server is running")
            print("   Start with: python manage.py runserver 8000")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n📖 Documentation:")
    print(f"   Full API docs: {base_url}/admin-dashboard/")
    print(f"   Django Admin: {base_url}/admin/")
    print(f"   System health check available at various endpoints")

if __name__ == "__main__":
    test_admin_endpoints()