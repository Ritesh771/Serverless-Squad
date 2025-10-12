#!/usr/bin/env python
"""
Script to setup test data for HomeServe Pro system testing
"""

import os
import django
import sys
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import User, Service

UserModel = get_user_model()

def create_test_services():
    """Create test services"""
    test_services = [
        {
            'name': 'AC Repair',
            'description': 'Air conditioner repair service',
            'base_price': Decimal('500.00'),
            'category': 'Appliances',
            'duration_minutes': 120,
            'is_active': True
        },
        {
            'name': 'Plumbing Service',
            'description': 'Plumbing repair and maintenance',
            'base_price': Decimal('300.00'),
            'category': 'Home Services',
            'duration_minutes': 90,
            'is_active': True
        },
        {
            'name': 'Electrical Work',
            'description': 'Electrical repair and installation',
            'base_price': Decimal('400.00'),
            'category': 'Home Services',
            'duration_minutes': 120,
            'is_active': True
        }
    ]

    created_services = []
    for service_data in test_services:
        # Check if service already exists
        if Service.objects.filter(name=service_data['name']).exists():
            print(f"Service {service_data['name']} already exists")
            continue
            
        # Create service
        try:
            service = Service.objects.create(**service_data)
            created_services.append(service)
            print(f"Created service: {service.name}")
        except Exception as e:
            print(f"Failed to create service {service_data['name']}: {e}")
    
    print(f"\nCreated {len(created_services)} test services")
    return created_services

def verify_test_setup():
    """Verify that test data is properly set up"""
    print("\n=== Test Data Verification ===")
    
    # Check users
    users = User.objects.filter(username__in=['customer1', 'vendor1', 'onboard_mgr', 'ops_mgr', 'admin'])
    print(f"Test users: {users.count()}")
    for user in users:
        print(f"  - {user.username} ({user.role})")
    
    # Check services
    services = Service.objects.filter(is_active=True)
    print(f"Active services: {services.count()}")
    for service in services:
        print(f"  - {service.name} ({service.category}) - ₹{service.base_price}")
    
    print("=== Verification Complete ===")

if __name__ == '__main__':
    print("Setting up test data for HomeServe Pro...")
    create_test_services()
    verify_test_setup()
    print("Done!")