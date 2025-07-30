#!/usr/bin/env python
"""
Script fix sequence IDs trong PostgreSQL
"""

import os
import sys
import django

# Thêm project path vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kho_my_pham.settings')

# Override database settings
os.environ['DATABASE_URL'] = 'postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham'

django.setup()

def fix_sequences():
    """Fix sequence IDs"""
    print("Fixing PostgreSQL sequences...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Fix sequences cho tất cả tables
            tables = [
                'accounts_profile',
                'products_category', 
                'products_product',
                'inventory_batch',
                'inventory_import',
                'inventory_importitem',
                'inventory_export',
                'inventory_exportitem',
                'auth_user',
                'django_admin_log',
                'django_content_type',
                'django_migrations',
                'django_session',
                'auth_group',
                'auth_permission',
                'auth_group_permissions',
                'auth_user_groups',
                'auth_user_user_permissions'
            ]
            
            for table in tables:
                try:
                    # Lấy max ID hiện tại
                    cursor.execute(f"SELECT MAX(id) FROM {table};")
                    result = cursor.fetchone()
                    max_id = result[0] if result[0] else 0
                    
                    # Reset sequence
                    cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), {max_id + 1}, false);")
                    
                    print(f"✅ Fixed sequence for {table}: max_id={max_id}, next_id={max_id + 1}")
                    
                except Exception as e:
                    print(f"⚠️  Warning for {table}: {e}")
            
            connection.commit()
            print("✅ All sequences fixed successfully!")
            
    except Exception as e:
        print(f"❌ Error fixing sequences: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_sequences() 