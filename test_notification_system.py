#!/usr/bin/env python
"""
Test script for the automated messaging and business alerts system.
Run this script to test various features of the notification system.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project root to the Python path
sys.path.append('/Users/riteshn/Desktop/Projects/Serverless-Squad')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')

# Setup Django
django.setup()

from django.utils import timezone
from core.models import (
    User, Service, Booking, NotificationLog, 
    PincodeAnalytics, BusinessAlert
)
from core.notification_service import NotificationService
from core.tasks import (
    generate_pincode_analytics, send_pincode_demand_alerts,
    send_vendor_bonus_alerts, send_promotional_campaigns,
    check_pending_signatures, test_notification_system
)


def create_test_data():
    """Create sample data for testing"""
    print("Creating test data...")
    
    # Create test users
    customer, created = User.objects.get_or_create(
        username='test_customer',
        defaults={
            'email': 'customer@test.com',
            'first_name': 'Test',
            'last_name': 'Customer',
            'role': 'customer',
            'pincode': '560001',
            'is_verified': True
        }
    )
    
    vendor1, created = User.objects.get_or_create(
        username='test_vendor1',
        defaults={
            'email': 'vendor1@test.com',
            'first_name': 'Test',
            'last_name': 'Vendor1',
            'role': 'vendor',
            'pincode': '560001',
            'is_available': True,
            'is_verified': True
        }
    )
    
    vendor2, created = User.objects.get_or_create(
        username='test_vendor2',
        defaults={
            'email': 'vendor2@test.com',
            'first_name': 'Test',
            'last_name': 'Vendor2',
            'role': 'vendor',
            'pincode': '560001',
            'is_available': True,
            'is_verified': True
        }
    )
    
    ops_manager, created = User.objects.get_or_create(
        username='test_ops_manager',
        defaults={
            'email': 'ops@test.com',
            'first_name': 'Ops',
            'last_name': 'Manager',
            'role': 'ops_manager',
            'is_staff': True,
            'is_verified': True
        }
    )
    
    # Create test service
    service, created = Service.objects.get_or_create(
        name='Plumbing Repair',
        defaults={
            'description': 'General plumbing repair service',
            'base_price': Decimal('500.00'),
            'category': 'plumbing',
            'duration_minutes': 120
        }
    )
    
    # Create test bookings
    for i in range(6):  # Create 6 bookings to trigger high demand
        booking = Booking.objects.create(
            customer=customer,
            vendor=vendor1 if i % 2 == 0 else vendor2,
            service=service,
            status='confirmed' if i < 3 else 'completed',
            total_price=Decimal('500.00'),
            pincode='560001',
            scheduled_date=timezone.now() + timedelta(hours=2 + i),
            completion_date=timezone.now() if i >= 3 else None
        )
    
    print(f"Created test data:")
    print(f"- Users: {User.objects.count()}")
    print(f"- Services: {Service.objects.count()}")
    print(f"- Bookings: {Booking.objects.count()}")


def test_pincode_analytics():
    """Test pincode analytics generation"""
    print("\n=== Testing Pincode Analytics ===")
    
    try:
        # Manually trigger analytics generation
        result = generate_pincode_analytics.delay()
        print(f"Analytics task started: {result.id}")
    except Exception as e:
        print(f"Redis not available, testing analytics generation directly: {e}")
        # Test the function directly without Celery
        from core.tasks import generate_pincode_analytics
        try:
            # Call the function directly
            result = generate_pincode_analytics()
            print(f"Analytics generated directly: {result}")
        except Exception as direct_error:
            print(f"Direct analytics generation failed: {direct_error}")
    
    # Check if analytics data was created
    analytics = PincodeAnalytics.objects.filter(
        pincode='560001',
        date=timezone.now().date()
    ).first()
    
    if analytics:
        print(f"Analytics created for pincode 560001:")
        print(f"- Total bookings: {analytics.total_bookings}")
        print(f"- Available vendors: {analytics.available_vendors}")
        print(f"- Demand ratio: {analytics.demand_ratio:.2f}")
        print(f"- Is high demand: {analytics.is_high_demand}")
    else:
        print("No analytics data found")


def test_demand_notifications():
    """Test demand-based notifications"""
    print("\n=== Testing Demand Notifications ===")
    
    try:
        # Manually trigger demand alerts
        result = send_pincode_demand_alerts.delay()
        print(f"Demand alerts task started: {result.id}")
    except Exception as e:
        print(f"Redis not available, testing notifications directly: {e}")
        # Test directly
        vendors = User.objects.filter(role='vendor', pincode='560001')
        if vendors.exists():
            demand_data = {
                'total_bookings': 6,
                'available_vendors': 2,
                'avg_booking_value': 500.0,
                'demand_ratio': 3.0
            }
            success = NotificationService.send_demand_notifications('560001', demand_data)
            print(f"Direct demand notification result: {success}")
    
    # Check notification logs
    recent_notifications = NotificationLog.objects.filter(
        notification_type='demand_notification',
        sent_at__gte=timezone.now() - timedelta(minutes=5)
    )
    
    print(f"Recent demand notifications: {recent_notifications.count()}")
    for notification in recent_notifications:
        print(f"- Sent to {notification.recipient.email}: {notification.status}")


def test_bonus_alerts():
    """Test vendor bonus alerts"""
    print("\n=== Testing Bonus Alerts ===")
    
    # Manually trigger bonus alerts
    result = send_vendor_bonus_alerts.delay()
    print(f"Bonus alerts task started: {result.id}")
    
    # Check notification logs
    recent_notifications = NotificationLog.objects.filter(
        notification_type='bonus_alert',
        sent_at__gte=timezone.now() - timedelta(minutes=5)
    )
    
    print(f"Recent bonus notifications: {recent_notifications.count()}")
    for notification in recent_notifications:
        print(f"- Sent to {notification.recipient.email}: {notification.status}")


def test_promotional_campaigns():
    """Test promotional campaigns"""
    print("\n=== Testing Promotional Campaigns ===")
    
    # Create a low-activity pincode for testing
    analytics, created = PincodeAnalytics.objects.get_or_create(
        pincode='560002',
        date=timezone.now().date(),
        defaults={
            'total_bookings': 1,  # Low activity
            'available_vendors': 2,
            'promotional_alert_sent': False
        }
    )
    
    # Manually trigger promotional campaigns
    result = send_promotional_campaigns.delay()
    print(f"Promotional campaigns task started: {result.id}")
    
    # Check notification logs
    recent_notifications = NotificationLog.objects.filter(
        notification_type='promotional',
        sent_at__gte=timezone.now() - timedelta(minutes=5)
    )
    
    print(f"Recent promotional notifications: {recent_notifications.count()}")
    for notification in recent_notifications:
        print(f"- Sent to {notification.recipient.email}: {notification.status}")


def test_business_alerts():
    """Test business alerts"""
    print("\n=== Testing Business Alerts ===")
    
    # Create a test business alert
    alert = BusinessAlert.objects.create(
        alert_type='system_error',
        severity='high',
        title='Test System Alert',
        description='This is a test alert created by the test script.',
        metadata={'test': True, 'timestamp': timezone.now().isoformat()}
    )
    
    print(f"Created test business alert: {alert.id}")
    
    # Test pending signatures check
    result = check_pending_signatures.delay()
    print(f"Pending signatures check started: {result.id}")
    
    # Check recent business alerts
    recent_alerts = BusinessAlert.objects.filter(
        created_at__gte=timezone.now() - timedelta(minutes=5)
    )
    
    print(f"Recent business alerts: {recent_alerts.count()}")
    for alert in recent_alerts:
        print(f"- {alert.alert_type}: {alert.title} (Severity: {alert.severity})")


def test_notification_service():
    """Test notification service methods"""
    print("\n=== Testing Notification Service ===")
    
    # Test demand notification
    vendors = User.objects.filter(role='vendor', pincode='560001')
    if vendors.exists():
        demand_data = {
            'total_bookings': 8,
            'available_vendors': 2,
            'avg_booking_value': 500.0,
            'demand_ratio': 4.0
        }
        
        success = NotificationService.send_demand_notifications('560001', demand_data)
        print(f"Demand notification sent: {success}")
    
    # Test bonus alerts
    success = NotificationService.send_bonus_alerts('560001', 15)
    print(f"Bonus alert sent: {success}")
    
    # Test promotional campaigns
    promotion_data = {
        'subject': 'Test Weekend Offer!',
        'title': 'Special Test Promotion',
        'description': 'This is a test promotional message.',
        'offer_text': '25% OFF',
        'offer_description': 'On all test services',
        'action_text': 'Book Test Service',
        'action_url': 'https://test.example.com/book',
        'expiry_date': 'Test Date'
    }
    
    success = NotificationService.location_based_promotions('560001', promotion_data)
    print(f"Promotional campaign sent: {success}")


def show_statistics():
    """Show current system statistics"""
    print("\n=== System Statistics ===")
    
    # Notification stats
    total_notifications = NotificationLog.objects.count()
    today_notifications = NotificationLog.objects.filter(
        sent_at__date=timezone.now().date()
    ).count()
    
    print(f"Total notifications sent: {total_notifications}")
    print(f"Notifications sent today: {today_notifications}")
    
    # Business alerts stats
    active_alerts = BusinessAlert.objects.filter(status='active').count()
    critical_alerts = BusinessAlert.objects.filter(
        status='active', 
        severity='critical'
    ).count()
    
    print(f"Active business alerts: {active_alerts}")
    print(f"Critical alerts: {critical_alerts}")
    
    # Pincode analytics stats
    analytics_count = PincodeAnalytics.objects.filter(
        date=timezone.now().date()
    ).count()
    
    print(f"Pincodes analyzed today: {analytics_count}")
    
    # User stats
    customers = User.objects.filter(role='customer').count()
    vendors = User.objects.filter(role='vendor').count()
    available_vendors = User.objects.filter(
        role='vendor', 
        is_available=True
    ).count()
    
    print(f"Total customers: {customers}")
    print(f"Total vendors: {vendors}")
    print(f"Available vendors: {available_vendors}")


def main():
    """Main test function"""
    print("🔔 Automated Messaging & Business Alerts System Test")
    print("=" * 55)
    
    print("\n📋 Note: This test demonstrates the notification system.")
    print("For full functionality, start Redis and Celery services:")
    print("1. Redis: redis-server")
    print("2. Celery Worker: celery -A homeserve_pro worker --loglevel=info")
    print("3. Celery Beat: celery -A homeserve_pro beat --loglevel=info")
    print("")
    
    try:
        # Create test data
        create_test_data()
        
        # Test pincode analytics
        test_pincode_analytics()
        
        # Test notification features
        test_demand_notifications()
        test_bonus_alerts()
        test_promotional_campaigns()
        
        # Test business alerts
        test_business_alerts()
        
        # Test notification service directly
        test_notification_service()
        
        # Show system statistics
        show_statistics()
        
        print("\n✅ All tests completed successfully!")
        print("\nTo view the results:")
        print("1. Check the Django admin at http://127.0.0.1:8000/admin/")
        print("2. Look at notification logs in admin dashboard")
        print("3. Check the homeserve_pro.log file for detailed logs")
        
        print("\nTo start Celery services:")
        print("Terminal 1: celery -A homeserve_pro worker --loglevel=info")
        print("Terminal 2: celery -A homeserve_pro beat --loglevel=info")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()