#!/usr/bin/env python
"""
Script test production settings locally
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
    'ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DATABASE_URL': 'postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham',
    'SECRET_KEY': 'django-insecure-u8&78e%ch+w(7#8a2nm)!$)+iihrx7h35e5pi-exh1z_w$=6se'
})

django.setup()

def test_production():
    """Test production settings locally"""
    print("🧪 Testing production settings locally...")
    print("=" * 50)
    
    try:
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Database connected: {version[0]}")
        
        # Test models
        from django.contrib.auth.models import User
        from products.models import Product, Category
        from inventory.models import Batch
        
        print(f"✅ Users: {User.objects.count()}")
        print(f"✅ Categories: {Category.objects.count()}")
        print(f"✅ Products: {Product.objects.count()}")
        print(f"✅ Batches: {Batch.objects.count()}")
        
        # Test static files
        from django.conf import settings
        print(f"✅ Static URL: {settings.STATIC_URL}")
        print(f"✅ Static Root: {settings.STATIC_ROOT}")
        print(f"✅ Debug: {settings.DEBUG}")
        print(f"✅ Allowed Hosts: {settings.ALLOWED_HOSTS}")
        
        # Test collectstatic
        print("\n📁 Testing collectstatic...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--dry-run'])
        
        print("\n✅ Production settings test completed successfully!")
        print("🚀 Ready for deployment!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_production() 