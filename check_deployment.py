#!/usr/bin/env python
"""
Script kiểm tra deployment status
"""

import requests
import os
import sys
import django

# Setup Django với production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')
os.environ.update({
    'DEBUG': 'False',
    'ALLOWED_HOSTS': 'khomypham.onrender.com',
    'DATABASE_URL': 'postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham',
    'SECRET_KEY': 'django-insecure-u8&78e%ch+w(7#8a2nm)!$)+iihrx7h35e5pi-exh1z_w$=6se'
})

django.setup()

def check_deployment():
    """Kiểm tra deployment"""
    url = "https://khomypham.onrender.com/"
    
    print(f"🔍 Checking deployment at: {url}")
    
    try:
        # Test basic connection
        response = requests.get(url, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Deployment is working!")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot connect to server")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Server is taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_health_endpoint():
    """Kiểm tra health endpoint"""
    url = "https://khomypham.onrender.com/health/"
    
    print(f"\n🔍 Checking health endpoint: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ Health Status: {response.status_code}")
        print(f"✅ Response: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def check_database():
    """Kiểm tra kết nối database"""
    print(f"\n🔍 Checking database connection...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Database connected: {version[0]}")
            
            # Kiểm tra số lượng records
            from django.contrib.auth.models import User
            from products.models import Product, Category
            from inventory.models import Batch
            
            print(f"✅ Users: {User.objects.count()}")
            print(f"✅ Categories: {Category.objects.count()}")
            print(f"✅ Products: {Product.objects.count()}")
            print(f"✅ Batches: {Batch.objects.count()}")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == '__main__':
    print("🚀 Deployment Check Tool")
    print("=" * 50)
    
    success = check_deployment()
    check_health_endpoint()
    check_database()
    
    if success:
        print("\n✅ Deployment is working correctly!")
        print("🌐 URL: https://khomypham.onrender.com/")
        print("👤 Admin: https://khomypham.onrender.com/admin/")
    else:
        print("\n❌ Deployment has issues!")
        print("🔧 Check Render.com logs for more details") 