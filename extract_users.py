#!/usr/bin/env python3
"""
Script to extract username and password information from the database
"""

import sqlite3
import os
import sys

def extract_user_credentials():
    """Extract username and password information from the database"""
    
    # Database path
    db_path = './db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    conn = None
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query to get user information
        query = """
        SELECT 
            id,
            username,
            email,
            first_name,
            last_name,
            password,
            role,
            is_active,
            is_verified,
            phone,
            pincode,
            date_joined,
            last_login
        FROM core_user 
        ORDER BY id
        """
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
            return
        
        print("=" * 80)
        print("USER CREDENTIALS EXTRACTED FROM DATABASE")
        print("=" * 80)
        print(f"Total users found: {len(users)}")
        print("-" * 80)
        
        # Column headers
        headers = [
            'ID', 'Username', 'Email', 'First Name', 'Last Name', 
            'Password Hash', 'Role', 'Active', 'Verified', 'Phone', 
            'Pincode', 'Date Joined', 'Last Login'
        ]
        
        # Print header
        print(f"{'ID':<4} {'Username':<15} {'Email':<25} {'Role':<15} {'Active':<8} {'Verified':<10}")
        print("-" * 80)
        
        # Print user data (excluding password hash for security)
        for user in users:
            user_id, username, email, first_name, last_name, password_hash, role, is_active, is_verified, phone, pincode, date_joined, last_login = user
            
            print(f"{user_id:<4} {username:<15} {email:<25} {role:<15} {is_active:<8} {is_verified:<10}")
        
        print("\n" + "=" * 80)
        print("DETAILED USER INFORMATION")
        print("=" * 80)
        
        # Print detailed information for each user
        for i, user in enumerate(users, 1):
            user_id, username, email, first_name, last_name, password_hash, role, is_active, is_verified, phone, pincode, date_joined, last_login = user
            
            print(f"\nUser #{i}:")
            print(f"  ID: {user_id}")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            print(f"  Full Name: {first_name} {last_name}")
            print(f"  Role: {role}")
            print(f"  Active: {is_active}")
            print(f"  Verified: {is_verified}")
            print(f"  Phone: {phone or 'N/A'}")
            print(f"  Pincode: {pincode or 'N/A'}")
            print(f"  Date Joined: {date_joined}")
            print(f"  Last Login: {last_login or 'Never'}")
            print(f"  Password Hash: {password_hash[:50]}..." if password_hash else "  Password Hash: None")
        
        print("\n" + "=" * 80)
        print("SECURITY NOTE:")
        print("Password hashes are Django's PBKDF2 format and cannot be reversed.")
        print("For testing purposes, you may need to reset passwords or use test credentials.")
        print("=" * 80)
        
        # Also save to file
        with open('user_credentials_export.txt', 'w') as f:
            f.write("USER CREDENTIALS EXPORT\n")
            f.write("=" * 50 + "\n")
            current_time = cursor.execute('SELECT datetime(\'now\')').fetchone()[0]
            f.write(f"Export Date: {current_time}\n")
            f.write(f"Total Users: {len(users)}\n\n")
            
            for i, user in enumerate(users, 1):
                user_id, username, email, first_name, last_name, password_hash, role, is_active, is_verified, phone, pincode, date_joined, last_login = user
                
                f.write(f"User #{i}:\n")
                f.write(f"  ID: {user_id}\n")
                f.write(f"  Username: {username}\n")
                f.write(f"  Email: {email}\n")
                f.write(f"  Full Name: {first_name} {last_name}\n")
                f.write(f"  Role: {role}\n")
                f.write(f"  Active: {is_active}\n")
                f.write(f"  Verified: {is_verified}\n")
                f.write(f"  Phone: {phone or 'N/A'}\n")
                f.write(f"  Pincode: {pincode or 'N/A'}\n")
                f.write(f"  Date Joined: {date_joined}\n")
                f.write(f"  Last Login: {last_login or 'Never'}\n")
                f.write(f"  Password Hash: {password_hash}\n")
                f.write("\n")
        
        print(f"\nExport saved to: user_credentials_export.txt")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    extract_user_credentials()