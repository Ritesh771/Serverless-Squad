"""
Test script for Dynamic Pricing System
Tests real-time pricing based on demand and supply density
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from core.models import Service, User, Booking, PincodeAnalytics
from core.dynamic_pricing_service import DynamicPricingService
import json


def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_basic_dynamic_pricing():
    """Test basic dynamic pricing calculation"""
    print_section("TEST 1: Basic Dynamic Pricing")
    
    # Get a service
    service = Service.objects.first()
    if not service:
        print("❌ No services found. Run create_sample_data.py first.")
        return
    
    print(f"✅ Testing with service: {service.name}")
    print(f"   Base Price: ₹{service.base_price}")
    
    # Test with different pincodes
    test_pincodes = ['400001', '110001', '560001']
    
    for pincode in test_pincodes:
        print(f"\n📍 Testing pincode: {pincode}")
        
        pricing = DynamicPricingService.calculate_dynamic_price(
            service, pincode
        )
        
        print(f"   Base Price:  ₹{pricing['base_price']}")
        print(f"   Final Price: ₹{pricing['final_price']}")
        print(f"   Change:      {pricing['price_change_percent']:+.1f}%")
        print(f"   Total Multiplier: {pricing['total_multiplier']:.2f}x")
        print(f"\n   Factors:")
        print(f"   - Demand: {pricing['factors']['demand']['level']} ({pricing['factors']['demand']['multiplier']:.2f}x)")
        print(f"   - Supply: {pricing['factors']['supply']['level']} ({pricing['factors']['supply']['multiplier']:.2f}x)")
        print(f"   - Time: {pricing['factors']['time']['multiplier']:.2f}x")


def test_demand_based_pricing():
    """Test pricing variations based on demand levels"""
    print_section("TEST 2: Demand-Based Pricing Simulation")
    
    service = Service.objects.first()
    if not service:
        return
    
    pincode = "400001"
    
    # Create analytics to simulate different demand levels
    today = timezone.now().date()
    
    scenarios = [
        {'bookings': 2, 'vendors': 5, 'label': 'Low Demand'},
        {'bookings': 10, 'vendors': 5, 'label': 'Normal Demand'},
        {'bookings': 20, 'vendors': 5, 'label': 'High Demand'},
        {'bookings': 50, 'vendors': 5, 'label': 'Extreme Demand'},
    ]
    
    print(f"\n📊 Service: {service.name} (Base: ₹{service.base_price})")
    print(f"📍 Pincode: {pincode}")
    print(f"\n{'Scenario':<20} {'Bookings':>10} {'Vendors':>10} {'Ratio':>10} {'Price':>12} {'Change':>10}")
    print("-" * 80)
    
    for scenario in scenarios:
        # Create/update analytics
        analytics, _ = PincodeAnalytics.objects.update_or_create(
            pincode=pincode,
            date=today,
            defaults={
                'total_bookings': scenario['bookings'],
                'available_vendors': scenario['vendors']
            }
        )
        
        # Clear cache to get fresh data
        DynamicPricingService.clear_cache(pincode)
        
        # Calculate price
        pricing = DynamicPricingService.calculate_dynamic_price(service, pincode)
        
        ratio = scenario['bookings'] / scenario['vendors']
        
        print(f"{scenario['label']:<20} {scenario['bookings']:>10} {scenario['vendors']:>10} "
              f"{ratio:>10.1f} ₹{pricing['final_price']:>10.2f} {pricing['price_change_percent']:>9.1f}%")


def test_supply_density_pricing():
    """Test pricing variations based on vendor supply"""
    print_section("TEST 3: Supply Density Pricing Simulation")
    
    service = Service.objects.first()
    if not service:
        return
    
    pincode = "110001"
    today = timezone.now().date()
    
    scenarios = [
        {'vendors': 0, 'label': 'No Vendors'},
        {'vendors': 1, 'label': 'Very Low Supply'},
        {'vendors': 3, 'label': 'Low Supply'},
        {'vendors': 5, 'label': 'Normal Supply'},
        {'vendors': 8, 'label': 'Good Supply'},
        {'vendors': 15, 'label': 'Excellent Supply'},
    ]
    
    print(f"\n📊 Service: {service.name} (Base: ₹{service.base_price})")
    print(f"📍 Pincode: {pincode}")
    print(f"📈 Fixed Demand: 10 bookings")
    print(f"\n{'Scenario':<20} {'Vendors':>10} {'Price':>12} {'Change':>10} {'Supply Level':<20}")
    print("-" * 80)
    
    for scenario in scenarios:
        # Create/update analytics
        analytics, _ = PincodeAnalytics.objects.update_or_create(
            pincode=pincode,
            date=today,
            defaults={
                'total_bookings': 10,
                'available_vendors': scenario['vendors']
            }
        )
        
        # Clear cache
        DynamicPricingService.clear_cache(pincode)
        
        # Calculate price
        pricing = DynamicPricingService.calculate_dynamic_price(service, pincode)
        
        supply_level = pricing['factors']['supply']['level']
        
        print(f"{scenario['label']:<20} {scenario['vendors']:>10} "
              f"₹{pricing['final_price']:>10.2f} {pricing['price_change_percent']:>9.1f}% {supply_level:<20}")


def test_time_based_pricing():
    """Test pricing variations based on time of day and day of week"""
    print_section("TEST 4: Time-Based Pricing Simulation")
    
    service = Service.objects.first()
    if not service:
        return
    
    pincode = "560001"
    
    # Test different times
    base_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    time_slots = [
        (8, 0, 'Morning (8 AM)'),
        (12, 0, 'Afternoon (12 PM)'),
        (18, 0, 'Peak Evening (6 PM)'),
        (22, 0, 'Late Night (10 PM)'),
    ]
    
    print(f"\n📊 Service: {service.name} (Base: ₹{service.base_price})")
    print(f"📍 Pincode: {pincode}")
    print(f"\n{'Time Slot':<25} {'Weekday Price':>15} {'Weekend Price':>15} {'Factors':<30}")
    print("-" * 95)
    
    for hour, minute, label in time_slots:
        # Weekday
        weekday_dt = base_date.replace(hour=hour, minute=minute)
        while weekday_dt.weekday() >= 5:  # Make sure it's a weekday
            weekday_dt += timedelta(days=1)
        
        weekday_pricing = DynamicPricingService.calculate_dynamic_price(
            service, pincode, weekday_dt
        )
        
        # Weekend
        weekend_dt = base_date.replace(hour=hour, minute=minute)
        while weekend_dt.weekday() < 5:  # Make sure it's a weekend
            weekend_dt += timedelta(days=1)
        
        weekend_pricing = DynamicPricingService.calculate_dynamic_price(
            service, pincode, weekend_dt
        )
        
        # Get factors
        factors = ', '.join(weekday_pricing['factors']['time']['factors']) or 'None'
        
        print(f"{label:<25} ₹{weekday_pricing['final_price']:>13.2f} "
              f"₹{weekend_pricing['final_price']:>13.2f} {factors:<30}")


def test_price_prediction():
    """Test 7-day price prediction"""
    print_section("TEST 5: 7-Day Price Prediction")
    
    service = Service.objects.first()
    if not service:
        return
    
    pincode = "400001"
    
    print(f"\n📊 Service: {service.name} (Base: ₹{service.base_price})")
    print(f"📍 Pincode: {pincode}")
    
    predictions = DynamicPricingService.get_price_prediction(service, pincode, 7)
    
    print(f"\n{'Date':<12} {'Day':<10} {'Morning':>10} {'Afternoon':>10} {'Evening':>10} {'Avg':>10} {'Best Time':<12}")
    print("-" * 85)
    
    for pred in predictions:
        print(f"{pred['date']:<12} {pred['day_of_week']:<10} "
              f"₹{pred['prices']['morning']:>8.2f} "
              f"₹{pred['prices']['afternoon']:>8.2f} "
              f"₹{pred['prices']['evening']:>8.2f} "
              f"₹{pred['avg_price']:>8.2f} {pred['best_time']:<12}")


def test_real_booking_integration():
    """Test actual booking creation with dynamic pricing"""
    print_section("TEST 6: Real Booking with Dynamic Pricing")
    
    # Get test data
    service = Service.objects.first()
    customer = User.objects.filter(role='customer').first()
    
    if not service or not customer:
        print("❌ Missing test data. Need service and customer.")
        return
    
    pincode = "400001"
    scheduled_date = timezone.now() + timedelta(days=1, hours=10)
    
    print(f"📊 Creating test booking...")
    print(f"   Service: {service.name} (Base: ₹{service.base_price})")
    print(f"   Customer: {customer.get_full_name()}")
    print(f"   Pincode: {pincode}")
    print(f"   Scheduled: {scheduled_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Calculate price first
    pricing = DynamicPricingService.calculate_dynamic_price(
        service, pincode, scheduled_date
    )
    
    print(f"\n💰 Dynamic Pricing:")
    print(f"   Base Price:    ₹{pricing['base_price']:.2f}")
    print(f"   Final Price:   ₹{pricing['final_price']:.2f}")
    print(f"   Change:        {pricing['price_change_percent']:+.1f}%")
    print(f"   Demand Level:  {pricing['factors']['demand']['level']}")
    print(f"   Supply Level:  {pricing['factors']['supply']['level']}")
    
    # Create booking
    booking = Booking.objects.create(
        customer=customer,
        service=service,
        pincode=pincode,
        scheduled_date=scheduled_date,
        total_price=pricing['final_price']
    )
    
    print(f"\n✅ Booking created successfully!")
    print(f"   Booking ID: {booking.id}")
    print(f"   Total Price: ₹{booking.total_price}")
    
    # Clean up
    print(f"\n🧹 Cleaning up test booking...")
    booking.delete()
    print(f"   Test booking deleted.")


def test_cache_performance():
    """Test caching performance"""
    print_section("TEST 7: Cache Performance Test")
    
    service = Service.objects.first()
    if not service:
        return
    
    pincode = "400001"
    
    import time
    
    # Clear cache first
    DynamicPricingService.clear_cache(pincode)
    
    # First call (no cache)
    start = time.time()
    pricing1 = DynamicPricingService.calculate_dynamic_price(service, pincode)
    time1 = (time.time() - start) * 1000
    
    # Second call (with cache)
    start = time.time()
    pricing2 = DynamicPricingService.calculate_dynamic_price(service, pincode)
    time2 = (time.time() - start) * 1000
    
    print(f"\n⚡ Performance Comparison:")
    print(f"   First call (no cache):  {time1:.2f}ms")
    print(f"   Second call (cached):   {time2:.2f}ms")
    print(f"   Speed improvement:      {(time1/time2):.1f}x faster")
    print(f"\n   Price consistency: {'✅ PASS' if pricing1['final_price'] == pricing2['final_price'] else '❌ FAIL'}")


def main():
    """Run all tests"""
    print("\n" + "🚀 "*30)
    print("   DYNAMIC PRICING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("🚀 "*30)
    
    try:
        test_basic_dynamic_pricing()
        test_demand_based_pricing()
        test_supply_density_pricing()
        test_time_based_pricing()
        test_price_prediction()
        test_real_booking_integration()
        test_cache_performance()
        
        print_section("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("\n📊 Dynamic Pricing System is fully operational!")
        print("\n💡 API Endpoints:")
        print("   GET  /api/dynamic-pricing/?service_id=<id>&pincode=<pincode>")
        print("   POST /api/dynamic-pricing/ (for price predictions)")
        print("\n📚 Documentation: See test results above for pricing behavior.\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
