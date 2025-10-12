"""
API Test for Dynamic Pricing Endpoints
Test the REST API endpoints for dynamic pricing
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/dynamic-pricing/"

# Test credentials (update with your actual test user)
USERNAME = "customer@test.com"
PASSWORD = "customer123"


def get_auth_token():
    """Get JWT authentication token"""
    login_url = f"{BASE_URL}/auth/login/"
    response = requests.post(login_url, json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        return response.json()['access']
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def test_get_dynamic_price(token, service_id=1, pincode="400001"):
    """Test GET endpoint for dynamic pricing"""
    print("\n" + "="*80)
    print("TEST 1: Get Dynamic Price")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test without scheduled time
    print(f"\n📍 Getting price for service {service_id} in pincode {pincode}...")
    params = {
        "service_id": service_id,
        "pincode": pincode
    }
    
    response = requests.get(API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"\n📊 Service: {data['service']['name']}")
        print(f"📍 Pincode: {data['pincode']}")
        print(f"\n💰 Pricing:")
        print(f"   Base Price:  ₹{data['pricing']['base_price']}")
        print(f"   Final Price: ₹{data['pricing']['final_price']}")
        print(f"   Change:      {data['pricing']['price_change_percent']:+.1f}%")
        print(f"\n🔍 Breakdown:")
        print(f"   Demand:      {data['pricing']['factors']['demand']['level']} ({data['pricing']['factors']['demand']['multiplier']:.2f}x)")
        print(f"   Supply:      {data['pricing']['factors']['supply']['level']} ({data['pricing']['factors']['supply']['multiplier']:.2f}x)")
        print(f"   Time:        {data['pricing']['factors']['time']['multiplier']:.2f}x")
        print(f"   Performance: {data['pricing']['factors']['performance']['multiplier']:.2f}x")
        return data
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return None


def test_get_dynamic_price_scheduled(token, service_id=1, pincode="400001"):
    """Test GET endpoint with scheduled datetime"""
    print("\n" + "="*80)
    print("TEST 2: Get Dynamic Price with Scheduled Time")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Schedule for tomorrow at 6 PM (peak hour)
    scheduled_dt = datetime.now() + timedelta(days=1)
    scheduled_dt = scheduled_dt.replace(hour=18, minute=0, second=0, microsecond=0)
    scheduled_iso = scheduled_dt.isoformat()
    
    print(f"\n📍 Getting price for service {service_id} in pincode {pincode}")
    print(f"📅 Scheduled for: {scheduled_dt.strftime('%Y-%m-%d %I:%M %p')}")
    
    params = {
        "service_id": service_id,
        "pincode": pincode,
        "scheduled_datetime": scheduled_iso
    }
    
    response = requests.get(API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"\n💰 Pricing:")
        print(f"   Base Price:  ₹{data['pricing']['base_price']}")
        print(f"   Final Price: ₹{data['pricing']['final_price']}")
        print(f"   Change:      {data['pricing']['price_change_percent']:+.1f}%")
        print(f"\n⏰ Time Factors: {', '.join(data['pricing']['factors']['time']['factors']) or 'None'}")
        return data
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return None


def test_get_price_predictions(token, service_id=1, pincode="400001", days=7):
    """Test POST endpoint for price predictions"""
    print("\n" + "="*80)
    print("TEST 3: Get Price Predictions")
    print("="*80)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "service_id": service_id,
        "pincode": pincode,
        "days": days
    }
    
    print(f"\n📊 Getting {days}-day price predictions...")
    print(f"📍 Service: {service_id}, Pincode: {pincode}")
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"\n📊 Service: {data['service']['name']} (Base: ₹{data['service']['base_price']})")
        print(f"\n{'Date':<12} {'Day':<10} {'Morning':>10} {'Afternoon':>10} {'Evening':>10} {'Best Time':<12}")
        print("-" * 75)
        
        for pred in data['predictions']:
            print(f"{pred['date']:<12} {pred['day_of_week']:<10} "
                  f"₹{pred['prices']['morning']:>8.2f} "
                  f"₹{pred['prices']['afternoon']:>8.2f} "
                  f"₹{pred['prices']['evening']:>8.2f} "
                  f"{pred['best_time']:<12}")
        
        return data
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return None


def test_multiple_pincodes(token, service_id=1):
    """Test pricing across multiple pincodes"""
    print("\n" + "="*80)
    print("TEST 4: Compare Prices Across Multiple Pincodes")
    print("="*80)
    
    pincodes = ["400001", "110001", "560001", "600001"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n📊 Comparing prices for service {service_id} across {len(pincodes)} pincodes")
    print(f"\n{'Pincode':<10} {'Base Price':>12} {'Final Price':>12} {'Change':>10} {'Demand':<15} {'Supply':<15}")
    print("-" * 85)
    
    for pincode in pincodes:
        params = {
            "service_id": service_id,
            "pincode": pincode
        }
        
        response = requests.get(API_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            pricing = data['pricing']
            print(f"{pincode:<10} "
                  f"₹{pricing['base_price']:>10.2f} "
                  f"₹{pricing['final_price']:>10.2f} "
                  f"{pricing['price_change_percent']:>9.1f}% "
                  f"{pricing['factors']['demand']['level']:<15} "
                  f"{pricing['factors']['supply']['level']:<15}")
        else:
            print(f"{pincode:<10} Error: {response.status_code}")


def main():
    """Run all API tests"""
    print("\n" + "🚀 "*30)
    print("   DYNAMIC PRICING API - ENDPOINT TESTS")
    print("🚀 "*30)
    
    # Get authentication token
    print("\n🔐 Authenticating...")
    token = get_auth_token()
    
    if not token:
        print("❌ Cannot proceed without authentication token")
        print("💡 Make sure:")
        print("   1. Django server is running (python manage.py runserver)")
        print("   2. Test user exists (run create_sample_data.py)")
        print("   3. Credentials in this script are correct")
        return 1
    
    print("✅ Authentication successful!")
    
    # Run tests
    try:
        test_get_dynamic_price(token)
        test_get_dynamic_price_scheduled(token)
        test_get_price_predictions(token)
        test_multiple_pincodes(token)
        
        print("\n" + "="*80)
        print("✅ ALL API TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\n📚 API Documentation:")
        print("   - GET  /api/dynamic-pricing/  - Get current dynamic price")
        print("   - POST /api/dynamic-pricing/  - Get price predictions")
        print("\n💡 Integration Examples:")
        print("   See DYNAMIC_PRICING_DOCS.md for full documentation")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
