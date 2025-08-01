#!/usr/bin/env python
"""
Script xóa dữ liệu database đơn giản sử dụng PostgreSQL
"""

import psycopg2
from dj_database_url import parse

# Database URL
DATABASE_URL = "postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham"

def clear_database_simple():
    """Xóa dữ liệu sử dụng SQL trực tiếp"""
    
    print("🔄 Bắt đầu xóa dữ liệu database...")
    print("=" * 50)
    
    try:
        # Parse DATABASE_URL
        db_config = parse(DATABASE_URL)
        
        # Kết nối database
        conn = psycopg2.connect(
            host=db_config['HOST'],
            port=db_config['PORT'],
            database=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD']
        )
        
        cursor = conn.cursor()
        
        # Thống kê trước khi xóa
        print("📊 Thống kê dữ liệu hiện tại:")
        
        tables = [
            ('auth_user', 'Users'),
            ('accounts_profile', 'Profiles'),
            ('products_category', 'Categories'),
            ('products_product', 'Products'),
            ('inventory_batch', 'Batches'),
            ('inventory_import', 'Imports'),
            ('inventory_importitem', 'Import Items'),
            ('inventory_export', 'Exports'),
            ('inventory_exportitem', 'Export Items')
        ]
        
        for table, name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"  - {name}: {count}")
        
        print()
        
        # Xác nhận từ người dùng
        confirm = input("⚠️  Bạn có chắc chắn muốn xóa tất cả dữ liệu? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Hủy bỏ thao tác.")
            return
        
        # Xóa dữ liệu theo thứ tự để tránh lỗi foreign key
        print("🗑️  Đang xóa dữ liệu...")
        
        # Xóa dữ liệu từ các bảng theo thứ tự phụ thuộc
        delete_queries = [
            ("DELETE FROM inventory_exportitem;", "Export Items"),
            ("DELETE FROM inventory_export;", "Exports"),
            ("DELETE FROM inventory_importitem;", "Import Items"),
            ("DELETE FROM inventory_import;", "Imports"),
            ("DELETE FROM inventory_batch;", "Batches"),
            ("DELETE FROM products_product;", "Products"),
            ("DELETE FROM products_category;", "Categories"),
            ("DELETE FROM accounts_profile;", "Profiles")
        ]
        
        for query, table_name in delete_queries:
            try:
                cursor.execute(query)
                print(f"  ✅ Đã xóa {table_name}")
            except Exception as e:
                print(f"  ⚠️  Lỗi khi xóa {table_name}: {e}")
                # Thử xóa với CASCADE nếu có lỗi foreign key
                try:
                    cascade_query = query.replace("DELETE FROM", "DELETE FROM").replace(";", " CASCADE;")
                    cursor.execute(cascade_query)
                    print(f"  ✅ Đã xóa {table_name} với CASCADE")
                except Exception as e2:
                    print(f"  ❌ Không thể xóa {table_name}: {e2}")
        
        # Reset sequences
        print()
        print("🔄 Đang reset sequences...")
        
        sequences = [
            ('products_category_id_seq', 'products_category'),
            ('products_product_id_seq', 'products_product'),
            ('inventory_batch_id_seq', 'inventory_batch'),
            ('inventory_import_id_seq', 'inventory_import'),
            ('inventory_importitem_id_seq', 'inventory_importitem'),
            ('inventory_export_id_seq', 'inventory_export'),
            ('inventory_exportitem_id_seq', 'inventory_exportitem'),
            ('accounts_profile_id_seq', 'accounts_profile')
        ]
        
        for seq_name, table_name in sequences:
            try:
                cursor.execute(f"SELECT setval('{seq_name}', 1, false);")
                print(f"  ✅ Reset sequence: {seq_name}")
            except Exception as e:
                print(f"  ⚠️  Không thể reset {seq_name}: {e}")
        
        # Commit thay đổi
        conn.commit()
        
        # Thống kê sau khi xóa
        print()
        print("📊 Thống kê sau khi xóa:")
        
        for table, name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            status = "(giữ nguyên)" if table == "auth_user" else ""
            print(f"  - {name}: {count} {status}")
        
        cursor.close()
        conn.close()
        
        print()
        print("🎉 Database đã được làm sạch thành công!")
        print("💡 Bạn có thể bắt đầu tạo lại dữ liệu từ đầu.")
        
    except Exception as e:
        print(f"❌ Lỗi khi xóa dữ liệu: {e}")
        return

if __name__ == "__main__":
    clear_database_simple() 