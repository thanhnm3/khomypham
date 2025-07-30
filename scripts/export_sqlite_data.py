#!/usr/bin/env python
"""
Script để export dữ liệu từ SQLite để backup
Sử dụng: python scripts/export_sqlite_data.py
"""

import os
import sys
import django
import json
from datetime import datetime
from django.core.management import execute_from_command_line

# Thêm project path vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Category, Product
from inventory.models import Batch, Import, ImportItem, Export, ExportItem
from accounts.models import Profile

def export_data():
    """Export dữ liệu từ SQLite"""
    print("Bắt đầu export dữ liệu...")
    
    # Tạo thư mục backup nếu chưa có
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'data_backup_{timestamp}.json')
    
    data = {
        'exported_at': datetime.now().isoformat(),
        'users': [],
        'profiles': [],
        'categories': [],
        'products': [],
        'batches': [],
        'imports': [],
        'import_items': [],
        'exports': [],
        'export_items': [],
    }
    
    # Export Users
    print("Exporting users...")
    for user in User.objects.all():
        data['users'].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat(),
        })
    
    # Export Profiles
    print("Exporting profiles...")
    for profile in Profile.objects.all():
        data['profiles'].append({
            'user_id': profile.user.id,
            'role': profile.role,
            'phone': profile.phone,
            'address': profile.address,
            'created_at': profile.created_at.isoformat(),
            'updated_at': profile.updated_at.isoformat(),
        })
    
    # Export Categories
    print("Exporting categories...")
    for category in Category.objects.all():
        data['categories'].append({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'created_at': category.created_at.isoformat(),
            'updated_at': category.updated_at.isoformat(),
        })
    
    # Export Products
    print("Exporting products...")
    for product in Product.objects.all():
        data['products'].append({
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'category_id': product.category.id,
            'unit': product.unit,
            'description': product.description,
            'is_active': product.is_active,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat(),
        })
    
    # Export Batches
    print("Exporting batches...")
    for batch in Batch.objects.all():
        data['batches'].append({
            'id': batch.id,
            'product_id': batch.product.id,
            'batch_code': batch.batch_code,
            'import_date': batch.import_date.isoformat(),
            'expiry_date': batch.expiry_date.isoformat(),
            'import_price': str(batch.import_price),
            'import_quantity': batch.import_quantity,
            'remaining_quantity': batch.remaining_quantity,
            'is_active': batch.is_active,
            'created_by_id': batch.created_by.id,
            'created_at': batch.created_at.isoformat(),
            'updated_at': batch.updated_at.isoformat(),
        })
    
    # Export Imports
    print("Exporting imports...")
    for import_order in Import.objects.all():
        data['imports'].append({
            'id': import_order.id,
            'import_code': import_order.import_code,
            'import_date': import_order.import_date.isoformat(),
            'supplier': import_order.supplier,
            'notes': import_order.notes,
            'created_by_id': import_order.created_by.id,
            'created_at': import_order.created_at.isoformat(),
            'updated_at': import_order.updated_at.isoformat(),
        })
    
    # Export Import Items
    print("Exporting import items...")
    for item in ImportItem.objects.all():
        data['import_items'].append({
            'id': item.id,
            'import_order_id': item.import_order.id,
            'product_id': item.product.id,
            'batch_code': item.batch_code,
            'quantity': item.quantity,
            'unit_price': str(item.unit_price),
            'expiry_date': item.expiry_date.isoformat(),
            'created_at': item.created_at.isoformat(),
        })
    
    # Export Exports
    print("Exporting exports...")
    for export_order in Export.objects.all():
        data['exports'].append({
            'id': export_order.id,
            'export_code': export_order.export_code,
            'export_date': export_order.export_date.isoformat(),
            'customer': export_order.customer,
            'notes': export_order.notes,
            'created_by_id': export_order.created_by.id,
            'created_at': export_order.created_at.isoformat(),
            'updated_at': export_order.updated_at.isoformat(),
        })
    
    # Export Export Items
    print("Exporting export items...")
    for item in ExportItem.objects.all():
        data['export_items'].append({
            'id': item.id,
            'export_order_id': item.export_order.id,
            'batch_id': item.batch.id,
            'quantity': item.quantity,
            'unit_price': str(item.unit_price),
            'created_at': item.created_at.isoformat(),
        })
    
    # Lưu file backup
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Export hoàn tất! File backup: {backup_file}")
    print(f"Tổng số records:")
    print(f"- Users: {len(data['users'])}")
    print(f"- Profiles: {len(data['profiles'])}")
    print(f"- Categories: {len(data['categories'])}")
    print(f"- Products: {len(data['products'])}")
    print(f"- Batches: {len(data['batches'])}")
    print(f"- Imports: {len(data['imports'])}")
    print(f"- Import Items: {len(data['import_items'])}")
    print(f"- Exports: {len(data['exports'])}")
    print(f"- Export Items: {len(data['export_items'])}")

if __name__ == '__main__':
    export_data() 