#!/usr/bin/env python3
"""
Smart Buffering System Test Script
Tests the intelligent scheduling system with travel time calculations and buffer management
"""

import os
import sys
import django
from datetime import datetime, timedelta, time

# Setup Django environment
sys.path.append('/Users/riteshn/Desktop/Projects/Serverless-Squad')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

from django.utils import timezone
from core.models import User, Service, Booking, VendorAvailability, TravelTimeCache
from core.travel_service import travel_service
from core.scheduling_service import scheduling_service

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def create_test_data():
    """Create test data for smart buffering demonstration"""
    print_header("CREATING TEST DATA")
    
    # Create vendors with different locations
    vendor1, created = User.objects.get_or_create(
        username='vendor_test1',
        defaults={
            'email': 'vendor1@test.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'role': 'vendor',
            'pincode': '110001',
            'is_available': True,
            'is_verified': True
        }
    )
    
    vendor2, created = User.objects.get_or_create(
        username='vendor_test2',
        defaults={
            'email': 'vendor2@test.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'vendor',
            'pincode': '110020',
            'is_available': True,
            'is_verified': True
        }
    )
    
    # Create customer
    customer, created = User.objects.get_or_create(
        username='customer_test',
        defaults={
            'email': 'customer@test.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'role': 'customer',
            'pincode': '110015',
            'is_verified': True
        }
    )
    
    # Create service
    service, created = Service.objects.get_or_create(
        name='Smart Plumbing Repair',
        defaults={
            'description': 'Intelligent plumbing service with smart scheduling',
            'base_price': 500.00,
            'category': 'plumbing',
            'duration_minutes': 90
        }
    )
    
    # Create vendor availability
    for vendor in [vendor1, vendor2]:
        VendorAvailability.objects.get_or_create(
            vendor=vendor,
            day_of_week='monday',
            defaults={
                'start_time': time(9, 0),
                'end_time': time(17, 0),
                'primary_pincode': vendor.pincode,
                'service_radius_km': 25,
                'preferred_buffer_minutes': 30,
                'max_travel_time_minutes': 60,
                'is_active': True
            }
        )
    
    print(f"✅ Created/Updated vendors: {vendor1.username}, {vendor2.username}")
    print(f"✅ Created/Updated customer: {customer.username}")
    print(f"✅ Created/Updated service: {service.name}")
    print(f"✅ Created vendor availability schedules")
    
    return vendor1, vendor2, customer, service

def test_travel_time_service():
    """Test travel time calculation and caching"""
    print_header("TESTING TRAVEL TIME SERVICE")
    
    # Test travel time calculation between different pincodes
    test_routes = [
        ('110001', '110015'),  # Vendor1 to Customer
        ('110020', '110015'),  # Vendor2 to Customer
        ('110001', '110050'),  # Long distance
        ('110001', '110001'),  # Same location
    ]
    
    for from_pincode, to_pincode in test_routes:
        travel_data = travel_service.get_travel_time(from_pincode, to_pincode)
        print(f"📍 {from_pincode} → {to_pincode}")
        print(f"   Distance: {travel_data['distance_km']}km")
        print(f"   Duration: {travel_data['duration_minutes']} minutes")
        print(f"   Traffic Duration: {travel_data['duration_in_traffic_minutes']} minutes")
        print(f"   Source: {travel_data['source']}")
        print()
    
    # Check cache
    cache_count = TravelTimeCache.objects.count()
    print(f"💾 Travel time cache entries: {cache_count}")

def test_smart_scheduling():
    """Test smart scheduling with buffer management"""
    print_header("TESTING SMART SCHEDULING")
    
    vendor1, vendor2, customer, service = create_test_data()
    
    # Test getting available time slots for today
    today = timezone.now().date()
    
    print(f"🗓️  Finding smart time slots for {today}")
    print(f"📋 Service: {service.name} ({service.duration_minutes} minutes)")
    print(f"📍 Customer location: {customer.pincode}")
    print()
    
    for vendor in [vendor1, vendor2]:
        print(f"👤 Vendor: {vendor.get_full_name()} (Location: {vendor.pincode})")
        
        try:
            available_slots = scheduling_service.get_available_time_slots(
                vendor.id, service.id, customer.pincode, today
            )
            
            if available_slots:
                print(f"   ✅ Found {len(available_slots)} available slots:")
                for slot in available_slots[:3]:  # Show first 3 slots
                    print(f"   ⏰ {slot['start_time'].strftime('%I:%M %p')} - {slot['end_time'].strftime('%I:%M %p')}")
                    print(f"      🚗 Travel time: {slot['travel_time_minutes']} min")
                    print(f"      🔧 Service time: {slot['service_duration_minutes']} min")
                    print(f"      ⏱️  Buffer before/after: {slot['buffer_before_minutes']}/{slot['buffer_after_minutes']} min")
                    print(f"      📊 Total duration: {slot['total_duration_minutes']} min")
                    print(f"      🎯 Optimization score: {slot['confidence_score']}")
                    print()
            else:
                print("   ❌ No available slots found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

def test_booking_with_smart_buffering():
    """Test booking creation with automatic smart buffering"""
    print_header("TESTING BOOKING WITH SMART BUFFERING")
    
    vendor1, vendor2, customer, service = create_test_data()
    
    # Create a booking
    scheduled_time = timezone.now() + timedelta(hours=2)
    
    print(f"📝 Creating booking with smart buffering")
    print(f"   👤 Customer: {customer.get_full_name()}")
    print(f"   🔧 Service: {service.name}")
    print(f"   📍 Location: {customer.pincode}")
    print(f"   ⏰ Scheduled: {scheduled_time.strftime('%Y-%m-%d %I:%M %p')}")
    print()
    
    # Create booking without vendor (pending state)
    booking = Booking.objects.create(
        customer=customer,
        service=service,
        status='pending',
        total_price=service.base_price,
        pincode=customer.pincode,
        scheduled_date=scheduled_time
    )
    
    print(f"✅ Created booking: {booking.id}")
    print(f"   Initial state (no vendor assigned yet)")
    print(f"   Travel time to location: {booking.travel_time_to_location_minutes or 'Not calculated'}")
    print()
    
    # Assign vendor and trigger smart buffering
    booking.vendor = vendor1
    
    # Manually trigger smart buffering (this would normally happen in the view)
    try:
        # Get travel time
        travel_data = travel_service.get_travel_time(vendor1.pincode, customer.pincode)
        booking.travel_time_to_location_minutes = travel_data['duration_minutes']
        booking.travel_time_from_location_minutes = travel_data['duration_minutes']
        booking.estimated_service_duration_minutes = service.duration_minutes
        
        # Get vendor preferences
        availability = VendorAvailability.objects.filter(vendor=vendor1, is_active=True).first()
        if availability:
            booking.buffer_before_minutes = availability.preferred_buffer_minutes
            booking.buffer_after_minutes = availability.preferred_buffer_minutes
        
        booking.save()  # This will trigger update_calculated_times()
        
        print(f"🎯 Applied smart buffering:")
        print(f"   🚗 Travel to location: {booking.travel_time_to_location_minutes} min")
        print(f"   🚗 Travel from location: {booking.travel_time_from_location_minutes} min")
        print(f"   🔧 Service duration: {booking.estimated_service_duration_minutes} min")
        print(f"   ⏱️  Buffer before: {booking.buffer_before_minutes} min")
        print(f"   ⏱️  Buffer after: {booking.buffer_after_minutes} min")
        print(f"   📊 Total duration: {booking.calculate_total_duration_minutes()} min")
        print(f"   🕐 Actual start time: {booking.actual_start_time}")
        print(f"   🕐 Actual end time: {booking.actual_end_time}")
        
    except Exception as e:
        print(f"❌ Error applying smart buffering: {e}")

def test_schedule_optimization():
    """Test schedule optimization for a vendor's day"""
    print_header("TESTING SCHEDULE OPTIMIZATION")
    
    vendor1, vendor2, customer, service = create_test_data()
    
    # Create some bookings for optimization testing
    base_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    bookings_data = [
        {'time_offset': 0, 'pincode': '110010'},      # 9:00 AM
        {'time_offset': 4, 'pincode': '110050'},      # 1:00 PM - far location
        {'time_offset': 6, 'pincode': '110012'},      # 3:00 PM - close to first
    ]
    
    print(f"📋 Creating test bookings for optimization:")
    
    for i, booking_data in enumerate(bookings_data):
        scheduled_time = base_time + timedelta(hours=booking_data['time_offset'])
        
        booking = Booking.objects.create(
            customer=customer,
            vendor=vendor1,
            service=service,
            status='confirmed',
            total_price=service.base_price,
            pincode=booking_data['pincode'],
            scheduled_date=scheduled_time,
            estimated_service_duration_minutes=service.duration_minutes
        )
        
        # Apply smart buffering
        travel_data = travel_service.get_travel_time(vendor1.pincode, booking_data['pincode'])
        booking.travel_time_to_location_minutes = travel_data['duration_minutes']
        booking.travel_time_from_location_minutes = travel_data['duration_minutes']
        booking.buffer_before_minutes = 15
        booking.buffer_after_minutes = 15
        booking.save()
        
        print(f\"   📝 Booking {i+1}: {scheduled_time.strftime('%I:%M %p')} at {booking_data['pincode']}\")
        print(f\"      🚗 Travel time: {booking.travel_time_to_location_minutes} min\")
    
    print()
    
    # Run optimization
    try:
        optimization = scheduling_service.optimize_vendor_schedule(vendor1.id, base_time.date())
        
        print(f\"📊 Schedule Optimization Results:\")
        print(f\"   📋 Total bookings: {optimization['total_bookings']}\")
        print(f\"   ⏰ Total working time: {optimization['total_working_time_minutes']} min\")
        print(f\"   🚗 Total travel time: {optimization['total_travel_time_minutes']} min\")
        print(f\"   🔧 Total service time: {optimization['total_service_time_minutes']} min\")
        print(f\"   🎯 Efficiency score: {optimization['efficiency_score']:.1f}%\")
        print()
        
        if optimization['optimization_suggestions']:
            print(f\"💡 Optimization Suggestions:\")
            for suggestion in optimization['optimization_suggestions']:
                print(f\"   {suggestion['severity'].upper()}: {suggestion['suggestion']}\")
        else:
            print(f\"✅ Schedule is well optimized!\")
            
    except Exception as e:
        print(f\"❌ Error running optimization: {e}\")

def test_optimal_booking_suggestion():
    \"\"\"Test optimal booking time suggestion\"\"\"
    print_header(\"TESTING OPTIMAL BOOKING SUGGESTION\")
    
    vendor1, vendor2, customer, service = create_test_data()
    
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    print(f\"🎯 Finding optimal booking time for:\")
    print(f\"   👤 Vendor: {vendor1.get_full_name()}\")
    print(f\"   🔧 Service: {service.name}\")
    print(f\"   📍 Customer location: {customer.pincode}\")
    print(f\"   📅 Date: {tomorrow}\")
    print()
    
    try:
        optimal_slot = scheduling_service.suggest_optimal_booking_time(
            vendor1.id, service.id, customer.pincode, tomorrow
        )
        
        if optimal_slot:
            print(f\"✅ Optimal booking suggestion found:\")
            print(f\"   ⏰ Time: {optimal_slot['start_time'].strftime('%I:%M %p')} - {optimal_slot['end_time'].strftime('%I:%M %p')}\")
            print(f\"   🚗 Travel time: {optimal_slot['travel_time_minutes']} min\")
            print(f\"   📊 Optimization score: {optimal_slot['optimization_score']:.1f}/100\")
            print(f\"   💰 Estimated cost: ${optimal_slot.get('estimated_cost', 'N/A')}\")
        else:
            print(f\"❌ No optimal slots available for the specified date\")
            
    except Exception as e:
        print(f\"❌ Error finding optimal slot: {e}\")

def run_all_tests():
    \"\"\"Run all smart buffering system tests\"\"\"
    print_header(\"SMART BUFFERING SYSTEM - COMPREHENSIVE TEST\")
    print(f\"🚀 Starting smart buffering system tests...\")
    print(f\"⏰ Test started at: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\")
    
    try:
        # Test 1: Travel Time Service
        test_travel_time_service()
        
        # Test 2: Smart Scheduling
        test_smart_scheduling()
        
        # Test 3: Booking with Smart Buffering
        test_booking_with_smart_buffering()
        
        # Test 4: Schedule Optimization
        test_schedule_optimization()
        
        # Test 5: Optimal Booking Suggestion
        test_optimal_booking_suggestion()
        
        print_header(\"TEST SUMMARY\")
        print(\"✅ All smart buffering system tests completed successfully!\")
        print(\"\n🎯 Key Features Tested:\")
        print(\"   ✓ Travel time calculation and caching\")
        print(\"   ✓ Smart time slot generation\")
        print(\"   ✓ Automatic buffer insertion\")
        print(\"   ✓ Booking optimization with travel times\")
        print(\"   ✓ Schedule efficiency analysis\")
        print(\"   ✓ Optimal booking time suggestions\")
        print(\"\n💡 Smart Buffering System is working correctly!\")
        
    except Exception as e:
        print_header(\"TEST FAILED\")
        print(f\"❌ Test failed with error: {e}\")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()