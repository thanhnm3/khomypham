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

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_env_file(file_path: str, override: bool = False) -> None:
    """Nạp biến môi trường từ file kiểu KEY=VALUE, bỏ qua dòng trống và comment (#)."""
    if not os.path.exists(file_path):
        return
    print(f"📄 Loading env from {os.path.basename(file_path)}")
    with open(file_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if not key:
                continue
            if override or key not in os.environ:
                os.environ[key] = value

# Ưu tiên dùng env_local.txt cho local; cho phép override để chắc chắn dùng DB local
load_env_file(os.path.join(ROOT_DIR, 'env_local.txt'), override=True)
# .env (nếu có) sẽ không override các biến đã có
load_env_file(os.path.join(ROOT_DIR, '.env'), override=False)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')

# DATABASE_URL, SECRET_KEY, ... sẽ được nạp từ env_local.txt / .env nếu tồn tại

django.setup()

def run_local():
    """Chạy ứng dụng local"""
    print("🚀 Starting Django development server...")
    # Hiển thị DB host để xác nhận đang dùng DB nào
    from dj_database_url import parse as parse_db_url
    db_url = os.environ.get('DATABASE_URL', '')
    try:
        cfg = parse_db_url(db_url) if db_url else {}
        db_host = cfg.get('HOST', 'unknown')
        print(f"📊 DATABASE_URL host: {db_host}")
    except Exception:
        pass
    print("🌐 URL: http://127.0.0.1:8000/")
    # Gợi ý: tạo superuser thủ công nếu cần: python manage.py createsuperuser
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

def backfill_profiles() -> None:
    from django.contrib.auth import get_user_model
    from accounts.models import Profile
    User = get_user_model()
    created_count = 0
    for user in User.objects.all():
        _, created = Profile.objects.get_or_create(user=user)
        if created:
            created_count += 1
    print(f"✅ Ensured profiles for all users. Created: {created_count}")

def create_user(username: str, password: str, is_superuser: bool = False) -> None:
    from django.contrib.auth import get_user_model
    from accounts.models import Profile
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    if is_superuser:
        user.is_staff = True
        user.is_superuser = True
    user.save()
    Profile.objects.get_or_create(user=user)
    print(f"✅ {'Created' if created else 'Updated'} user '{username}'")

if __name__ == '__main__':
    # CLI đơn giản: chạy lệnh quản lý sau khi nạp env_local.txt / .env
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'migrate':
            execute_from_command_line(['manage.py', 'migrate'])
        elif cmd == 'backfill_profiles':
            backfill_profiles()
        elif cmd == 'create_user' and len(sys.argv) >= 4:
            username = sys.argv[2]
            password = sys.argv[3]
            is_super = ('--superuser' in sys.argv[4:])
            create_user(username, password, is_super)
        else:
            # pass-through bất kỳ lệnh khác của manage.py
            execute_from_command_line(['manage.py'] + sys.argv[1:])
    else:
        run_local()