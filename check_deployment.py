#!/usr/bin/env python3
"""
Script để kiểm tra deployment và dependencies
"""

import sys
import importlib
import requests

def check_dependency(module_name, package_name=None):
    """Kiểm tra một dependency có được cài đặt không"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError:
        print(f"❌ {package_name or module_name} - MISSING")
        return False

def check_django_settings():
    """Kiểm tra cấu hình Django"""
    try:
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        
        print("\n🔧 Django Settings Check:")
        print(f"✅ DEBUG = {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
        print(f"✅ STATIC_ROOT = {settings.STATIC_ROOT}")
        print(f"✅ DATABASES = {list(settings.DATABASES.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Django Settings Error: {e}")
        return False

def check_static_files():
    """Kiểm tra static files"""
    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line
        
        # Chạy collectstatic để kiểm tra
        execute_from_command_line(['manage.py', 'collectstatic', '--dry-run', '--noinput'])
        print("✅ Static files collection - OK")
        return True
    except Exception as e:
        print(f"❌ Static files Error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Kho My Pham - Deployment Check")
    print("=" * 50)
    
    # Danh sách dependencies cần kiểm tra
    dependencies = [
        ('django', 'Django'),
        ('PIL', 'Pillow'),
        ('openpyxl', 'openpyxl'),
        ('reportlab', 'reportlab'),
        ('crispy_forms', 'django-crispy-forms'),
        ('crispy_bootstrap5', 'crispy-bootstrap5'),
        ('psycopg2', 'psycopg2-binary'),
        ('decouple', 'python-decouple'),
        ('dj_database_url', 'dj-database-url'),
        ('whitenoise', 'whitenoise'),
        ('requests', 'requests'),
        ('pandas', 'pandas'),
        ('xlrd', 'xlrd'),
    ]
    
    # Dependencies chỉ cần thiết cho production
    production_dependencies = [
        ('gunicorn', 'gunicorn'),
    ]
    
    print("\n📦 Dependencies Check:")
    print("-" * 30)
    
    all_ok = True
    for module, package in dependencies:
        if not check_dependency(module, package):
            all_ok = False
    
    print("\n📦 Production Dependencies Check:")
    print("-" * 40)
    
    production_ok = True
    for module, package in production_dependencies:
        if not check_dependency(module, package):
            print(f"⚠️  {package} - MISSING (chỉ cần cho production)")
            production_ok = False
        else:
            print(f"✅ {package} - OK")
    
    # Kiểm tra Django settings
    django_ok = check_django_settings()
    
    # Kiểm tra static files
    static_ok = check_static_files()
    
    print("\n" + "=" * 50)
    if all_ok and django_ok and static_ok:
        print("🎉 Tất cả kiểm tra đều PASSED!")
        print("✅ Ứng dụng sẵn sàng để deploy")
        if not production_ok:
            print("⚠️  Lưu ý: Một số dependencies production chưa được cài đặt")
            print("   (Điều này bình thường trong môi trường development)")
    else:
        print("⚠️  Có một số vấn đề cần khắc phục:")
        if not all_ok:
            print("   - Thiếu một số dependencies")
        if not django_ok:
            print("   - Lỗi cấu hình Django")
        if not static_ok:
            print("   - Lỗi static files")
        print("\n💡 Hãy cài đặt các dependencies thiếu:")
        print("   pip install -r requirements_production.txt")
    
    return all_ok and django_ok and static_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 