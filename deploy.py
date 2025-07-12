#!/usr/bin/env python
"""
Deployment script for Railway/Production
This script handles database setup and migrations
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_vehiculos.settings')
    
    # Set production environment
    os.environ.setdefault('DEBUG', 'False')
    
    django.setup()
    
    print("🚀 Starting deployment process...")
    
    # Run migrations
    print("📦 Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Collect static files
    print("📁 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Create superuser if specified
    if os.environ.get('DJANGO_SUPERUSER_USERNAME'):
        print("👤 Creating superuser...")
        try:
            execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
        except Exception as e:
            print(f"Superuser creation skipped: {e}")
    
    print("✅ Deployment completed successfully!")
