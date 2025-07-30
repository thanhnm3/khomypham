#!/usr/bin/env python
"""
Script tạo superuser trên PostgreSQL
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Thêm project path vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')

# Override database settings
os.environ['DATABASE_URL'] = 'postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham'

django.setup()

def create_superuser():
    """Tạo superuser"""
    print("Creating superuser...")
    
    try:
        from django.contrib.auth.models import User
        
        # Kiểm tra xem đã có superuser chưa
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superuser already exists!")
            return
        
        # Tạo superuser
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print(f"✅ Superuser created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

if __name__ == '__main__':
    create_superuser() 