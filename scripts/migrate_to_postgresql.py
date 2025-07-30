#!/usr/bin/env python
"""
Script để migrate dữ liệu từ SQLite sang PostgreSQL
Sử dụng: python scripts/migrate_to_postgresql.py
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Thêm project path vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')
django.setup()

def migrate_to_postgresql():
    """Migrate dữ liệu từ SQLite sang PostgreSQL"""
    print("Bắt đầu migrate dữ liệu sang PostgreSQL...")
    
    # 1. Tạo migrations nếu chưa có
    print("1. Tạo migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # 2. Migrate database
    print("2. Chạy migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # 3. Tạo superuser nếu cần
    print("3. Tạo superuser...")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
    except:
        print("Superuser đã tồn tại hoặc có lỗi khi tạo")
    
    # 4. Collect static files
    print("4. Collect static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    print("Migrate hoàn tất!")

if __name__ == '__main__':
    migrate_to_postgresql() 