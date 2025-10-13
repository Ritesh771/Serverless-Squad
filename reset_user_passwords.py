#!/usr/bin/env python
"""
Script to reset user passwords for testing purposes
"""

import os
import django
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
django.setup()

from core.models import User
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist

def reset_passwords():
    """Reset passwords for all users with a common test password"""
    
    # Common test password
    test_password = "password123"
    
    print("🔐 PASSWORD RESET UTILITY")
    print("=" * 50)
    print(f"Setting password '{test_password}' for all users...")
    print()
    
    users = User.objects.all()
    reset_count = 0
    
    for user in users:
        try:
            # Use Django's set_password method which handles hashing
            user.set_password(test_password)
            user.save()
            
            print(f"✅ User '{user.username}' ({user.email}) - Password reset")
            reset_count += 1
            
        except Exception as e:
            print(f"❌ Error resetting password for '{user.username}': {str(e)}")
    
    print()
    print("=" * 50)
    print(f"✅ Password reset complete! {reset_count} users updated.")
    print()
    print("📝 LOGIN CREDENTIALS:")
    print(f"   Username: [any username from the list]")
    print(f"   Password: {test_password}")
    print()
    print("🔑 Available usernames:")
    
    # List all usernames for easy reference
    usernames = User.objects.all().values_list('username', 'role', 'email')
    for username, role, email in usernames:
        print(f"   • {username} ({role}) - {email}")

def reset_specific_user():
    """Reset password for a specific user"""
    print("\n🎯 RESET SPECIFIC USER")
    print("=" * 30)
    
    username = input("Enter username: ").strip()
    new_password = input("Enter new password (or press Enter for 'password123'): ").strip()
    
    if not new_password:
        new_password = "password123"
    
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        
        print(f"✅ Password updated for '{username}'")
        print(f"   New password: {new_password}")
        
    except ObjectDoesNotExist:
        print(f"❌ User '{username}' not found")
        
        print("\n📋 Available users:")
        users = User.objects.all().values_list('username', flat=True)
        for user in users:
            print(f"   • {user}")

def main():
    print("🔐 HomeServe Pro - Password Reset Utility")
    print("=" * 50)
    print("1. Reset all users to 'password123'")
    print("2. Reset specific user")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        confirm = input("\n⚠️  Are you sure you want to reset ALL user passwords? (y/N): ").strip().lower()
        if confirm == 'y':
            reset_passwords()
        else:
            print("❌ Operation cancelled")
            
    elif choice == "2":
        reset_specific_user()
        
    elif choice == "3":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()