#!/usr/bin/env python
"""
Script to reset MFA for admin user
Run this to delete all MFA devices for admin: python reset_mfa.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice

try:
    user = User.objects.get(username='admin')
    
    devices = TOTPDevice.objects.filter(user=user)
    device_count = devices.count()
    
    if device_count > 0:
        print(f"Found {device_count} MFA device(s) for admin user:")
        for device in devices:
            print(f"  - ID: {device.id}, Name: {device.name}, Confirmed: {device.confirmed}")
        
        TOTPDevice.objects.filter(user=user).delete()
        print(f"\n✓ Successfully deleted {device_count} MFA device(s).")
        print("Admin will be required to set up MFA on next login.")
    else:
        print("No MFA devices found for admin user.")
        print("MFA is already reset.")
        
except User.DoesNotExist:
    print("Error: Admin user not found!")
    print("Please create the admin user first using: python create_admin.py")
