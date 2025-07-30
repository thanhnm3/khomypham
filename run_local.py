#!/usr/bin/env python
"""
Script chạy ứng dụng local với PostgreSQL
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

# Thêm project path vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')

# Override database settings cho PostgreSQL
os.environ['DATABASE_URL'] = 'postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham'

django.setup()

def run_local():
    """Chạy ứng dụng local"""
    print("🚀 Starting Django development server with PostgreSQL...")
    print("📊 Database: PostgreSQL on Render.com")
    print("🌐 URL: http://127.0.0.1:8000/")
    print("👤 Admin login: admin / admin123")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Test database connection trước
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Database connected: {version[0]}")
        
        # Chạy server
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    run_local() 