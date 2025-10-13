#!/usr/bin/env python
"""
Quick reference for test user credentials after password reset
"""

print("🔐 HOMESERVE PRO - TEST USER CREDENTIALS")
print("=" * 60)
print()
print("After running 'python reset_user_passwords.py', all users will have:")
print("Password: password123")
print()
print("📋 USER ROLES & TEST ACCOUNTS:")
print("-" * 40)
print()

# Based on your user export data
test_accounts = [
    ("CUSTOMERS", [
        ("Ritesh", "riturithesh7@gmail.com", "Main customer account"),
        ("customer1", "customer1@example.com", "Alice Johnson"),
        ("customer2", "customer2@example.com", "Bob Smith"),
        ("customer3", "customer3@example.com", "Catherine Williams"),
        ("customer4", "customer4@example.com", "Daniel Brown"),
        ("customer5", "customer5@example.com", "Emily Davis"),
    ]),
    ("ADMINS", [
        ("admin", "admin@gmail.com", "Basic admin"),
        ("admin1", "admin1@homeservepro.com", "John Admin"),
        ("admin2", "admin2@homeservepro.com", "Sarah Administrator"),
        ("admin3", "admin3@homeservepro.com", "Michael SuperAdmin"),
    ]),
    ("OPERATIONS MANAGERS", [
        ("ops1", "ops1@homeservepro.com", "Emma Operations"),
        ("ops2", "ops2@homeservepro.com", "David Manager"),
        ("ops3", "ops3@homeservepro.com", "Lisa Ops"),
    ]),
    ("ONBOARD MANAGERS", [
        ("onboard1", "onboard1@homeservepro.com", "James Onboarding"),
        ("onboard2", "onboard2@homeservepro.com", "Sophia Recruiter"),
        ("onboard3", "onboard3@homeservepro.com", "William Manager"),
    ]),
    ("VENDORS", [
        ("vendor1", "vendor1@example.com", "Robert Plumber"),
        ("vendor2", "vendor2@example.com", "Maria Electrician"),
        ("vendor3", "vendor3@example.com", "Carlos Carpenter"),
        ("vendor4", "vendor4@example.com", "Jennifer HVAC"),
    ]),
]

for role, users in test_accounts:
    print(f"🏷️  {role}:")
    for username, email, name in users:
        print(f"   Username: {username:<12} | Email: {email:<25} | {name}")
    print()

print("💡 QUICK LOGIN EXAMPLES:")
print("-" * 30)
print("Customer Login:")
print("  Username: customer1")
print("  Password: password123")
print()
print("Admin Login:")
print("  Username: admin1")
print("  Password: password123")
print()
print("Vendor Login:")
print("  Username: vendor1")
print("  Password: password123")
print()

print("🚀 TO RESET PASSWORDS:")
print("-" * 25)
print("Run: python reset_user_passwords.py")
print()
print("🌐 LOGIN ENDPOINTS:")
print("-" * 20)
print("Frontend: http://localhost:5173/login")
print("Backend API: http://localhost:8000/auth/login/")
print("Django Admin: http://localhost:8000/admin/")
print()
print("📱 TEST THE SYSTEM:")
print("-" * 20)
print("1. Start backend: python manage.py runserver")
print("2. Start frontend: npm run dev")
print("3. Use any username above with password: password123")