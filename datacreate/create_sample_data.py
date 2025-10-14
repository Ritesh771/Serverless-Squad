#!/usr/bin/env python
"""Sample data creation script for HomeServe Pro"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

from core.models import User, Service, Booking
from django.utils import timezone
from datetime import timedelta
import random

def create_sample_data():
    print("Creating sample data for HomeServe Pro...")
    
    # Create Services
    services_data = [
        {'name': 'AC Repair', 'description': 'Air conditioning repair and maintenance', 'base_price': 500, 'category': 'Appliance', 'duration_minutes': 120},
        {'name': 'Plumbing Service', 'description': 'Professional plumbing services', 'base_price': 400, 'category': 'Home Maintenance', 'duration_minutes': 90},
        {'name': 'Electrical Work', 'description': 'Electrical repairs and installations', 'base_price': 600, 'category': 'Electrical', 'duration_minutes': 150},
        {'name': 'House Cleaning', 'description': 'Professional house cleaning service', 'base_price': 300, 'category': 'Cleaning', 'duration_minutes': 180},
        {'name': 'Appliance Repair', 'description': 'Washing machine, refrigerator repairs', 'base_price': 450, 'category': 'Appliance', 'duration_minutes': 100},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults=service_data
        )
        if created:
            print(f"✓ Created service: {service.name}")
    
    # Create sample users
    users_data = [
        {'username': 'customer1', 'email': 'customer1@test.com', 'role': 'customer', 'first_name': 'John', 'last_name': 'Doe', 'phone': '+919876543210', 'pincode': '110001'},
        {'username': 'customer2', 'email': 'customer2@test.com', 'role': 'customer', 'first_name': 'Jane', 'last_name': 'Smith', 'phone': '+919876543211', 'pincode': '110002'},
        {'username': 'vendor1', 'email': 'vendor1@test.com', 'role': 'vendor', 'first_name': 'Mike', 'last_name': 'Wilson', 'phone': '+919876543212', 'pincode': '110001', 'is_available': True, 'is_verified': True},
        {'username': 'vendor2', 'email': 'vendor2@test.com', 'role': 'vendor', 'first_name': 'Sarah', 'last_name': 'Johnson', 'phone': '+919876543213', 'pincode': '110002', 'is_available': True, 'is_verified': True},
        {'username': 'onboard_mgr', 'email': 'onboard@test.com', 'role': 'onboard_manager', 'first_name': 'Alice', 'last_name': 'Brown', 'is_verified': True},
        {'username': 'ops_mgr', 'email': 'ops@test.com', 'role': 'ops_manager', 'first_name': 'Bob', 'last_name': 'Davis', 'is_verified': True},
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.is_verified = user_data.get('is_verified', True)
            user.save()
            print(f"✓ Created user: {user.username} ({user.role})")
    
    print("Sample data created successfully!")

if __name__ == '__main__':
    create_sample_data()