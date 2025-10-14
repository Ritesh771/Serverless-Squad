#!/usr/bin/env python
"""
Simple migration script for HomeServe Pro
"""

import os
import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')

def run_migrations():
    try:
        # Import Django after setting the environment
        import django
        django.setup()
        
        # Import management commands
        from django.core.management import execute_from_command_line
        
        print("Running Django migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("Migrations completed successfully!")
        
    except Exception as e:
        print(f"Error running migrations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_migrations()