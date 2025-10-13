

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.hashers import make_password
from core.models import (
    User, Service, Booking, Address, VendorAvailability,
    Payment, Signature, Photo, VendorApplication, VendorDocument,
    Earnings, PerformanceMetrics, PincodeAnalytics
)


def create_users():
    """Create users for each role"""
    print("Creating users...")
    
    users = []
    
    # Super Admins
    super_admins = [
        {
            'username': 'admin1',
            'email': 'admin1@homeservepro.com',
            'first_name': 'John',
            'last_name': 'Admin',
            'role': 'super_admin',
            'phone': '+1234567890',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'admin2',
            'email': 'admin2@homeservepro.com',
            'first_name': 'Sarah',
            'last_name': 'Administrator',
            'role': 'super_admin',
            'phone': '+1234567891',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'admin3',
            'email': 'admin3@homeservepro.com',
            'first_name': 'Michael',
            'last_name': 'SuperAdmin',
            'role': 'super_admin',
            'phone': '+1234567892',
            'is_verified': True,
            'is_available': True
        },
    ]
    
    # Ops Managers
    ops_managers = [
        {
            'username': 'ops1',
            'email': 'ops1@homeservepro.com',
            'first_name': 'Emma',
            'last_name': 'Operations',
            'role': 'ops_manager',
            'phone': '+1234567893',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'ops2',
            'email': 'ops2@homeservepro.com',
            'first_name': 'David',
            'last_name': 'Manager',
            'role': 'ops_manager',
            'phone': '+1234567894',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'ops3',
            'email': 'ops3@homeservepro.com',
            'first_name': 'Lisa',
            'last_name': 'Ops',
            'role': 'ops_manager',
            'phone': '+1234567895',
            'is_verified': True,
            'is_available': True
        },
    ]
    
    # Onboard Managers
    onboard_managers = [
        {
            'username': 'onboard1',
            'email': 'onboard1@homeservepro.com',
            'first_name': 'James',
            'last_name': 'Onboarding',
            'role': 'onboard_manager',
            'phone': '+1234567896',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'onboard2',
            'email': 'onboard2@homeservepro.com',
            'first_name': 'Sophia',
            'last_name': 'Recruiter',
            'role': 'onboard_manager',
            'phone': '+1234567897',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'onboard3',
            'email': 'onboard3@homeservepro.com',
            'first_name': 'William',
            'last_name': 'Manager',
            'role': 'onboard_manager',
            'phone': '+1234567898',
            'is_verified': True,
            'is_available': True
        },
    ]
    
    # Vendors
    vendors = [
        {
            'username': 'vendor1',
            'email': 'vendor1@example.com',
            'first_name': 'Robert',
            'last_name': 'Plumber',
            'role': 'vendor',
            'phone': '+1234567899',
            'pincode': '400001',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'vendor2',
            'email': 'vendor2@example.com',
            'first_name': 'Maria',
            'last_name': 'Electrician',
            'role': 'vendor',
            'phone': '+1234567800',
            'pincode': '400002',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'vendor3',
            'email': 'vendor3@example.com',
            'first_name': 'Carlos',
            'last_name': 'Carpenter',
            'role': 'vendor',
            'phone': '+1234567801',
            'pincode': '400003',
            'is_verified': True,
            'is_available': True
        },
        {
            'username': 'vendor4',
            'email': 'vendor4@example.com',
            'first_name': 'Jennifer',
            'last_name': 'HVAC',
            'role': 'vendor',
            'phone': '+1234567802',
            'pincode': '400001',
            'is_verified': True,
            'is_available': True
        },
    ]
    
    # Customers
    customers = [
        {
            'username': 'customer1',
            'email': 'customer1@example.com',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'role': 'customer',
            'phone': '+1234567803',
            'pincode': '400001',
            'is_verified': True
        },
        {
            'username': 'customer2',
            'email': 'customer2@example.com',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'role': 'customer',
            'phone': '+1234567804',
            'pincode': '400002',
            'is_verified': True
        },
        {
            'username': 'customer3',
            'email': 'customer3@example.com',
            'first_name': 'Catherine',
            'last_name': 'Williams',
            'role': 'customer',
            'phone': '+1234567805',
            'pincode': '400003',
            'is_verified': True
        },
        {
            'username': 'customer4',
            'email': 'customer4@example.com',
            'first_name': 'Daniel',
            'last_name': 'Brown',
            'role': 'customer',
            'phone': '+1234567806',
            'pincode': '400001',
            'is_verified': True
        },
        {
            'username': 'customer5',
            'email': 'customer5@example.com',
            'first_name': 'Emily',
            'last_name': 'Davis',
            'role': 'customer',
            'phone': '+1234567807',
            'pincode': '400002',
            'is_verified': True
        },
    ]
    
    all_users = super_admins + ops_managers + onboard_managers + vendors + customers
    
    for user_data in all_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                **user_data,
                'password': make_password('password123')  # Default password for all users
            }
        )
        if created:
            print(f"✅ Created {user_data['role']}: {user_data['username']}")
        else:
            print(f"ℹ️  {user_data['role']} {user_data['username']} already exists")
        users.append(user)
    
    return users


def create_services():
    """Create service categories"""
    print("\nCreating services...")
    
    services_data = [
        {
            'name': 'Plumbing Repair',
            'description': 'Fix leaks, unclog drains, repair pipes',
            'base_price': Decimal('75.00'),
            'category': 'Plumbing',
            'duration_minutes': 60
        },
        {
            'name': 'Emergency Plumbing',
            'description': 'Emergency plumbing services available 24/7',
            'base_price': Decimal('150.00'),
            'category': 'Plumbing',
            'duration_minutes': 90
        },
        {
            'name': 'Electrical Wiring',
            'description': 'Install new wiring, fix electrical issues',
            'base_price': Decimal('100.00'),
            'category': 'Electrical',
            'duration_minutes': 120
        },
        {
            'name': 'Light Fixture Installation',
            'description': 'Install ceiling fans, chandeliers, light fixtures',
            'base_price': Decimal('60.00'),
            'category': 'Electrical',
            'duration_minutes': 45
        },
        {
            'name': 'Carpentry Work',
            'description': 'Custom woodwork, furniture repair, door installation',
            'base_price': Decimal('90.00'),
            'category': 'Carpentry',
            'duration_minutes': 90
        },
        {
            'name': 'Cabinet Installation',
            'description': 'Install kitchen and bathroom cabinets',
            'base_price': Decimal('200.00'),
            'category': 'Carpentry',
            'duration_minutes': 180
        },
        {
            'name': 'HVAC Maintenance',
            'description': 'Air conditioning and heating system maintenance',
            'base_price': Decimal('120.00'),
            'category': 'HVAC',
            'duration_minutes': 75
        },
        {
            'name': 'AC Repair',
            'description': 'Diagnose and repair air conditioning issues',
            'base_price': Decimal('150.00'),
            'category': 'HVAC',
            'duration_minutes': 90
        },
        {
            'name': 'House Cleaning',
            'description': 'Deep cleaning services for your home',
            'base_price': Decimal('80.00'),
            'category': 'Cleaning',
            'duration_minutes': 120
        },
        {
            'name': 'Painting Service',
            'description': 'Interior and exterior painting',
            'base_price': Decimal('200.00'),
            'category': 'Painting',
            'duration_minutes': 240
        },
    ]
    
    services = []
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults=service_data
        )
        if created:
            print(f"✅ Created service: {service_data['name']}")
        services.append(service)
    
    return services


def create_addresses(customers):
    """Create addresses for customers"""
    print("\nCreating addresses...")
    
    address_templates = [
        {'label': 'Home', 'address_line': '123 Main Street, Apartment 4B', 'pincode': '400001'},
        {'label': 'Office', 'address_line': '456 Business Park, Suite 200', 'pincode': '400002'},
        {'label': 'Parents Home', 'address_line': '789 Oak Avenue', 'pincode': '400003'},
    ]
    
    addresses = []
    for customer in customers:
        for i, addr_template in enumerate(address_templates[:2]):  # 2 addresses per customer
            address, created = Address.objects.get_or_create(
                user=customer,
                label=addr_template['label'],
                defaults={
                    'address_line': addr_template['address_line'],
                    'pincode': addr_template.get('pincode', customer.pincode or '400001'),
                    'is_default': i == 0
                }
            )
            if created:
                print(f"✅ Created address for {customer.username}: {addr_template['label']}")
            addresses.append(address)
    
    return addresses


def create_vendor_availability(vendors, services):
    """Create vendor availability records"""
    print("\nCreating vendor availability...")
    
    from datetime import time
    
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    
    for vendor in vendors:
        # Create availability slots for each day
        for day in days_of_week:
            availability, created = VendorAvailability.objects.get_or_create(
                vendor=vendor,
                day_of_week=day,
                start_time=time(8, 0),
                defaults={
                    'primary_pincode': vendor.pincode,
                    'service_radius_km': random.choice([5, 10, 15, 20]),
                    'preferred_buffer_minutes': random.choice([15, 30, 45]),
                    'end_time': time(18, 0),   # 6:00 PM
                    'is_active': True
                }
            )
            
            if created and day == 'monday':  # Print only once per vendor
                print(f"✅ Created availability for vendor: {vendor.username}")


def create_bookings(customers, vendors, services, addresses):
    """Create sample bookings"""
    print("\nCreating bookings...")
    
    statuses = ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']
    
    bookings = []
    for i in range(15):  # Create 15 bookings
        customer = random.choice(customers)
        vendor = random.choice(vendors) if i % 3 != 0 else None  # Some bookings without vendor
        service = random.choice(services)
        
        # Create booking datetime within last 30 days or next 30 days
        days_offset = random.randint(-30, 30)
        hours = random.randint(8, 17)
        scheduled_datetime = timezone.now() + timedelta(days=days_offset, hours=hours - timezone.now().hour)
        scheduled_datetime = scheduled_datetime.replace(minute=0, second=0, microsecond=0)
        
        status = random.choice(statuses)
        
        # Calculate total price with some variation
        total_price = service.base_price * Decimal(random.uniform(0.9, 1.2))
        
        booking_data = {
            'customer': customer,
            'service': service,
            'pincode': customer.pincode or '400001',
            'scheduled_date': scheduled_datetime,
            'status': status,
            'total_price': round(total_price, 2),
            'estimated_service_duration_minutes': service.duration_minutes,
        }
        
        if vendor:
            booking_data['vendor'] = vendor
        
        if status == 'completed':
            booking_data['completion_date'] = timezone.now() - timedelta(days=random.randint(1, 10))
        
        booking = Booking.objects.create(**booking_data)
        bookings.append(booking)
        print(f"✅ Created booking #{str(booking.id)[:8]}... - {status}")
    
    return bookings


def create_payments(bookings):
    """Create payments for completed bookings"""
    print("\nCreating payments...")
    
    completed_bookings = [b for b in bookings if b.status == 'completed']
    
    for booking in completed_bookings:
        amount = booking.total_price
        
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': amount,
                'status': random.choice(['pending', 'completed', 'processing']),
                'payment_type': random.choice(['automatic', 'manual']),
            }
        )
        
        if created:
            print(f"✅ Created payment for booking {str(booking.id)[:8]}...")


def create_vendor_applications(vendors, onboard_managers):
    """Create vendor applications"""
    print("\nCreating vendor applications...")
    
    for i, vendor in enumerate(vendors[:3]):  # First 3 vendors
        application, created = VendorApplication.objects.get_or_create(
            email=vendor.email,
            defaults={
                'name': f"{vendor.first_name} {vendor.last_name}",
                'phone': vendor.phone or '+1234567899',
                'pincode': vendor.pincode or '400001',
                'service_category': random.choice(['Plumbing', 'Electrical', 'Carpentry', 'HVAC']),
                'experience': random.randint(2, 15),
                'id_proof': f'/documents/id_proof_{i}.pdf',
                'address_proof': f'/documents/address_proof_{i}.pdf',
                'profile_photo': f'/documents/profile_{i}.jpg',
                'status': 'approved',
                'vendor_account': vendor,
                'reviewed_by': random.choice(onboard_managers),
                'reviewed_at': timezone.now() - timedelta(days=random.randint(10, 60))
            }
        )
        
        if created:
            print(f"✅ Created application for vendor: {vendor.username}")


def create_vendor_documents(vendors):
    """Create vendor document records (without actual files)"""
    print("\nSkipping vendor documents (requires file uploads)...")
    # Skip creating documents as they require actual file uploads


def create_earnings(vendors):
    """Create earnings records for vendors"""
    print("\nCreating earnings...")
    
    for vendor in vendors:
        # Create earnings for last 3 months
        for month_offset in range(3):
            date = timezone.now().date() - timedelta(days=30 * month_offset)
            
            earnings, created = Earnings.objects.get_or_create(
                vendor=vendor,
                date=date.replace(day=1),
                defaults={
                    'total_bookings': random.randint(5, 25),
                    'completed_bookings': random.randint(3, 20),
                    'total_revenue': Decimal(random.uniform(500, 3000)),
                    'platform_fee': Decimal(random.uniform(50, 300)),
                    'net_earnings': Decimal(random.uniform(450, 2700))
                }
            )
            
            if created:
                print(f"✅ Created earnings for {vendor.username} - {date.strftime('%B %Y')}")


def create_performance_metrics(vendors):
    """Create performance metrics for vendors"""
    print("\nCreating performance metrics...")
    
    for vendor in vendors:
        metrics, created = PerformanceMetrics.objects.get_or_create(
            vendor=vendor,
            defaults={
                'total_bookings': random.randint(10, 100),
                'completed_bookings': random.randint(8, 90),
                'cancelled_bookings': random.randint(0, 5),
                'average_rating': Decimal(random.uniform(3.5, 5.0)),
                'response_time_minutes': random.randint(10, 120),
                'completion_rate': Decimal(random.uniform(0.85, 0.99))
            }
        )
        
        if created:
            print(f"✅ Created performance metrics for {vendor.username}")


def create_pincode_analytics():
    """Create pincode analytics data"""
    print("\nCreating pincode analytics...")
    
    pincodes = ['400001', '400002', '400003', '400004', '400005']
    
    for pincode in pincodes:
        for days_ago in range(7):
            date = timezone.now().date() - timedelta(days=days_ago)
            
            analytics, created = PincodeAnalytics.objects.get_or_create(
                pincode=pincode,
                date=date,
                defaults={
                    'total_bookings': random.randint(5, 30),
                    'completed_bookings': random.randint(3, 25),
                    'cancelled_bookings': random.randint(0, 5),
                    'active_vendors': random.randint(2, 10),
                    'active_customers': random.randint(5, 20),
                    'average_response_time_minutes': random.randint(15, 90),
                    'demand_score': Decimal(random.uniform(0.5, 1.0)),
                    'supply_score': Decimal(random.uniform(0.4, 0.9))
                }
            )
            
            if created and days_ago == 0:
                print(f"✅ Created analytics for pincode: {pincode}")


def main():
    """Main function to populate all data"""
    print("=" * 60)
    print("POPULATING DATABASE WITH SAMPLE DATA")
    print("=" * 60)
    
    # Create all data
    users = create_users()
    services = create_services()
    
    # Filter users by role
    customers = [u for u in users if u.role == 'customer']
    vendors = [u for u in users if u.role == 'vendor']
    onboard_managers = [u for u in users if u.role == 'onboard_manager']
    ops_managers = [u for u in users if u.role == 'ops_manager']
    super_admins = [u for u in users if u.role == 'super_admin']
    
    addresses = create_addresses(customers)
    create_vendor_availability(vendors, services)
    bookings = create_bookings(customers, vendors, services, addresses)
    create_payments(bookings)
    create_vendor_applications(vendors, onboard_managers)
    create_vendor_documents(vendors)
    create_earnings(vendors)
    create_performance_metrics(vendors)
    create_pincode_analytics()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE POPULATED SUCCESSFULLY!")
    print("=" * 60)
    print("\nUser Accounts Summary:")
    print(f"  🔑 Super Admins: {len(super_admins)}")
    print(f"  👔 Ops Managers: {len(ops_managers)}")
    print(f"  📋 Onboard Managers: {len(onboard_managers)}")
    print(f"  🔧 Vendors: {len(vendors)}")
    print(f"  👤 Customers: {len(customers)}")
    print(f"\n  📦 Services: {Service.objects.count()}")
    print(f"  📅 Bookings: {Booking.objects.count()}")
    print(f"  🏠 Addresses: {Address.objects.count()}")
    print(f"  💰 Payments: {Payment.objects.count()}")
    print("\nDefault Password for all users: password123")
    print("=" * 60)


if __name__ == '__main__':
    main()
