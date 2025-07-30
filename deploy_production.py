#!/usr/bin/env python
"""
Script deploy production với cấu hình đúng
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Thêm project path vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django với production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')

# Production environment variables
os.environ.update({
    'DEBUG': 'False',
    'ALLOWED_HOSTS': 'khomypham.onrender.com,localhost,127.0.0.1',
    'DATABASE_URL': 'postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham',
    'SECRET_KEY': 'django-insecure-u8&78e%ch+w(7#8a2nm)!$)+iihrx7h35e5pi-exh1z_w$=6se'
})

django.setup()

def deploy_production():
    """Deploy production"""
    print("🚀 Deploying to production...")
    
    try:
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Database connected: {version[0]}")
        
        # Run migrations
        print("📊 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        # Create superuser if not exists
        print("👤 Checking superuser...")
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
            print("✅ Superuser created")
        else:
            print("✅ Superuser already exists")
        
        print("✅ Production deployment completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    deploy_production() 