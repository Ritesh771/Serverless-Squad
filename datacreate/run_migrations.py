#!/usr/bin/env python
"""
Script to run database migrations for HomeServe Pro
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def run_migration_commands():
    """Run the migration commands with proper environment setup"""
    print("Setting up environment...")
    
    # Add current directory to Python path
    project_dir = Path(__file__).parent
    sys.path.insert(0, str(project_dir))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')
    
    print("Current working directory:", os.getcwd())
    print("Project directory:", project_dir)
    
    try:
        # Try direct Django approach
        print("Setting up Django...")
        import django
        from django.core.management import execute_from_command_line
        
        django.setup()
        print("Django setup complete")
        
        # Run migrations
        print("Running makemigrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("Running migrate...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("Database migrations completed successfully!")
        
    except Exception as e:
        print(f"Direct Django approach failed: {e}")
        print("Trying subprocess approach...")
        
        # Try subprocess approach
        try:
            python_exe = sys.executable
            print(f"Using Python executable: {python_exe}")
            
            # Run makemigrations
            print("Running makemigrations via subprocess...")
            makemigrations_result = subprocess.run([
                python_exe, 'manage.py', 'makemigrations'
            ], capture_output=True, text=True, timeout=60)
            
            print(f"makemigrations stdout: {makemigrations_result.stdout}")
            if makemigrations_result.stderr:
                print(f"makemigrations stderr: {makemigrations_result.stderr}")
            print(f"makemigrations return code: {makemigrations_result.returncode}")
            
            # Run migrate
            print("Running migrate via subprocess...")
            migrate_result = subprocess.run([
                python_exe, 'manage.py', 'migrate'
            ], capture_output=True, text=True, timeout=60)
            
            print(f"migrate stdout: {migrate_result.stdout}")
            if migrate_result.stderr:
                print(f"migrate stderr: {migrate_result.stderr}")
            print(f"migrate return code: {migrate_result.returncode}")
            
            if migrate_result.returncode == 0:
                print("Database migrations completed successfully!")
            else:
                print("Migration failed. Check output above for details.")
                
        except Exception as sub_e:
            print(f"Subprocess approach also failed: {sub_e}")

if __name__ == '__main__':
    run_migration_commands()