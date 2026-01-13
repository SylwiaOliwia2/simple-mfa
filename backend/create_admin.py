#!/usr/bin/env python
"""
Script to create admin user with username 'admin' and password 'admin'
Run this after migrations: python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Create admin user if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '', 'admin')
    print("Admin user created successfully!")
    print("Username: admin")
    print("Password: admin")
else:
    print("Admin user already exists!")
