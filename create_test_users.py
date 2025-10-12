#!/usr/bin/env python
"""
Script to create test users for HomeServe Pro system testing
"""

import os
import django
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import User

UserModel = get_user_model()

def create_test_users():
    """Create test users for all roles"""
    test_users = [
        {
            'username': 'customer1',
            'email': 'customer1@test.com',
            'password': 'password123',
            'role': 'customer',
            'first_name': 'Customer',
            'last_name': 'One',
            'pincode': '110001',
            'phone': '+919876543210'
        },
        {
            'username': 'vendor1',
            'email': 'vendor1@test.com',
            'password': 'password123',
            'role': 'vendor',
            'first_name': 'Vendor',
            'last_name': 'One',
            'pincode': '110001',
            'phone': '+919876543211',
            'is_available': True,
            'is_verified': True
        },
        {
            'username': 'onboard_mgr',
            'email': 'onboard@test.com',
            'password': 'password123',
            'role': 'onboard_manager',
            'first_name': 'Onboard',
            'last_name': 'Manager',
            'phone': '+919876543212'
        },
        {
            'username': 'ops_mgr',
            'email': 'ops@test.com',
            'password': 'password123',
            'role': 'ops_manager',
            'first_name': 'Ops',
            'last_name': 'Manager',
            'phone': '+919876543213'
        },
        {
            'username': 'admin',
            'email': 'admin@test.com',
            'password': 'password123',
            'role': 'super_admin',
            'first_name': 'Super',
            'last_name': 'Admin',
            'phone': '+919876543214'
        }
    ]

    created_users = []
    for user_data in test_users:
        username = user_data['username']
        password = user_data['password']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"User {username} already exists")
            continue
            
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password=password,
                role=user_data['role'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data.get('phone', ''),
                pincode=user_data.get('pincode', ''),
                is_available=user_data.get('is_available', False),
                is_verified=user_data.get('is_verified', False)
            )
            created_users.append(user)
            print(f"Created user: {username} ({user_data['role']})")
        except Exception as e:
            print(f"Failed to create user {username}: {e}")
    
    print(f"\nCreated {len(created_users)} test users")
    return created_users

if __name__ == '__main__':
    print("Creating test users for HomeServe Pro...")
    create_test_users()
    print("Done!")