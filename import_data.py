#!/usr/bin/env python
"""
Script import dữ liệu từ backup JSON vào PostgreSQL
"""

import os
import sys
import json
import django
from datetime import datetime

# Thêm project path vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')

# Override database settings
os.environ['DATABASE_URL'] = 'postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham'

django.setup()

def import_data():
    """Import dữ liệu từ backup"""
    print("Importing data from backup...")
    
    try:
        # Tìm file backup mới nhất
        backup_dir = os.path.join(os.path.dirname(__file__), 'backup')
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
        
        if not backup_files:
            print("❌ No backup files found!")
            return
        
        # Lấy file mới nhất
        latest_backup = max(backup_files, key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
        backup_file = os.path.join(backup_dir, latest_backup)
        
        print(f"Using backup file: {latest_backup}")
        
        # Load backup data
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        from django.contrib.auth.models import User
        from products.models import Category, Product
        from inventory.models import Batch, Import, ImportItem, Export, ExportItem
        from accounts.models import Profile
        
        # 1. Import Users
        print("Importing users...")
        for user_data in data['users']:
            user, created = User.objects.get_or_create(
                id=user_data['id'],
                defaults={
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data['is_staff'],
                    'is_superuser': user_data['is_superuser'],
                    'is_active': user_data['is_active'],
                    'date_joined': datetime.fromisoformat(user_data['date_joined']),
                }
            )
            if created:
                print(f"  ✅ Created user: {user.username}")
        
        # 2. Import Categories
        print("Importing categories...")
        for cat_data in data['categories']:
            category, created = Category.objects.get_or_create(
                id=cat_data['id'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'created_at': datetime.fromisoformat(cat_data['created_at']),
                    'updated_at': datetime.fromisoformat(cat_data['updated_at']),
                }
            )
            if created:
                print(f"  ✅ Created category: {category.name}")
        
        # 3. Import Products
        print("Importing products...")
        for prod_data in data['products']:
            product, created = Product.objects.get_or_create(
                id=prod_data['id'],
                defaults={
                    'code': prod_data['code'],
                    'name': prod_data['name'],
                    'category_id': prod_data['category_id'],
                    'unit': prod_data['unit'],
                    'description': prod_data['description'],
                    'is_active': prod_data['is_active'],
                    'created_at': datetime.fromisoformat(prod_data['created_at']),
                    'updated_at': datetime.fromisoformat(prod_data['updated_at']),
                }
            )
            if created:
                print(f"  ✅ Created product: {product.name}")
        
        # 4. Import Profiles
        print("Importing profiles...")
        for profile_data in data['profiles']:
            profile, created = Profile.objects.get_or_create(
                user_id=profile_data['user_id'],
                defaults={
                    'role': profile_data['role'],
                    'phone': profile_data['phone'],
                    'address': profile_data['address'],
                    'created_at': datetime.fromisoformat(profile_data['created_at']),
                    'updated_at': datetime.fromisoformat(profile_data['updated_at']),
                }
            )
            if created:
                print(f"  ✅ Created profile for user: {profile.user.username}")
        
        # 5. Import Batches
        print("Importing batches...")
        for batch_data in data['batches']:
            batch, created = Batch.objects.get_or_create(
                id=batch_data['id'],
                defaults={
                    'product_id': batch_data['product_id'],
                    'batch_code': batch_data['batch_code'],
                    'import_date': datetime.fromisoformat(batch_data['import_date']).date(),
                    'expiry_date': datetime.fromisoformat(batch_data['expiry_date']).date(),
                    'import_price': batch_data['import_price'],
                    'import_quantity': batch_data['import_quantity'],
                    'remaining_quantity': batch_data['remaining_quantity'],
                    'is_active': batch_data['is_active'],
                    'created_by_id': batch_data['created_by_id'],
                    'created_at': datetime.fromisoformat(batch_data['created_at']),
                    'updated_at': datetime.fromisoformat(batch_data['updated_at']),
                }
            )
            if created:
                print(f"  ✅ Created batch: {batch.batch_code}")
        
        # 6. Import Imports
        print("Importing imports...")
        for import_data in data['imports']:
            import_order, created = Import.objects.get_or_create(
                id=import_data['id'],
                defaults={
                    'import_code': import_data['import_code'],
                    'import_date': datetime.fromisoformat(import_data['import_date']),
                    'supplier': import_data['supplier'],
                    'notes': import_data['notes'],
                    'created_by_id': import_data['created_by_id'],
                    'created_at': datetime.fromisoformat(import_data['created_at']),
                    'updated_at': datetime.fromisoformat(import_data['updated_at']),
                }
            )
            if created:
                print(f"  ✅ Created import: {import_order.import_code}")
        
        # 7. Import Import Items
        print("Importing import items...")
        for item_data in data['import_items']:
            item, created = ImportItem.objects.get_or_create(
                id=item_data['id'],
                defaults={
                    'import_order_id': item_data['import_order_id'],
                    'product_id': item_data['product_id'],
                    'batch_code': item_data['batch_code'],
                    'quantity': item_data['quantity'],
                    'unit_price': item_data['unit_price'],
                    'expiry_date': datetime.fromisoformat(item_data['expiry_date']).date(),
                    'created_at': datetime.fromisoformat(item_data['created_at']),
                }
            )
            if created:
                print(f"  ✅ Created import item: {item.product.name}")
        
        # 8. Import Exports
        print("Importing exports...")
        for export_data in data['exports']:
            export_order, created = Export.objects.get_or_create(
                id=export_data['id'],
                defaults={
                    'export_code': export_data['export_code'],
                    'export_date': datetime.fromisoformat(export_data['export_date']),
                    'customer': export_data['customer'],
                    'notes': export_data['notes'],
                    'created_by_id': export_data['created_by_id'],
                    'created_at': datetime.fromisoformat(export_data['created_at']),
                    'updated_at': datetime.fromisoformat(export_data['updated_at']),
                }
            )
            if created:
                print(f"  ✅ Created export: {export_order.export_code}")
        
        # 9. Import Export Items
        print("Importing export items...")
        for item_data in data['export_items']:
            item, created = ExportItem.objects.get_or_create(
                id=item_data['id'],
                defaults={
                    'export_order_id': item_data['export_order_id'],
                    'batch_id': item_data['batch_id'],
                    'quantity': item_data['quantity'],
                    'unit_price': item_data['unit_price'],
                    'created_at': datetime.fromisoformat(item_data['created_at']),
                }
            )
            if created:
                print(f"  ✅ Created export item: {item.batch.product.name}")
        
        print("✅ Data import completed successfully!")
        
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import_data() 