# Hướng dẫn Test Local với PostgreSQL

## Tóm tắt
Hướng dẫn test ứng dụng kho mỹ phẩm local với PostgreSQL database trên Render.com.

## Thông tin Database
- **Host**: `dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com`
- **Database**: `khomypham`
- **Username**: `khomypham_user`
- **Password**: `t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd`

## Bước 1: Chuẩn bị môi trường

### Cài đặt dependencies
```bash
cd kho_my_pham
pip install -r requirements.txt
```

### Tạo file .env (tùy chọn)
Tạo file `.env` trong thư mục `kho_my_pham`:
```bash
# Django Settings
SECRET_KEY=django-insecure-u8&78e%ch+w(7#8a2nm)!$)+iihrx7h35e5pi-exh1z_w$=6se
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DATABASE_URL=postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham
```

## Bước 2: Test kết nối database

### Test kết nối cơ bản
```bash
python test_db.py
```

Kết quả mong đợi:
```
✅ Connection successful!
PostgreSQL version: PostgreSQL 17.5...
Available databases:
  - khomypham
  - template1
  - template0
```

### Test ứng dụng
```bash
python test_app.py
```

Kết quả mong đợi:
```
✅ Users: 3
✅ Categories: 9
✅ Products: 3
✅ Batches: 2
✅ Imports: 2
✅ Exports: 1
✅ Profiles: 3
```

## Bước 3: Chạy ứng dụng local

### Cách 1: Sử dụng script tự động
```bash
python run_local.py
```

### Cách 2: Chạy thủ công
```bash
# Set environment variable
set DATABASE_URL=postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham

# Chạy server
python manage.py runserver
```

## Bước 4: Test các chức năng

### Truy cập ứng dụng
- **URL**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

### Đăng nhập
- **Username**: `admin`
- **Password**: `admin123`

### Test các chức năng chính

#### 1. Quản lý sản phẩm
- Truy cập: http://127.0.0.1:8000/products/
- Kiểm tra danh sách sản phẩm
- Thêm/sửa/xóa sản phẩm

#### 2. Quản lý kho
- **Nhập kho**: http://127.0.0.1:8000/inventory/imports/
- **Xuất kho**: http://127.0.0.1:8000/inventory/exports/
- Kiểm tra tạo phiếu nhập/xuất

#### 3. Báo cáo
- **Tồn kho**: http://127.0.0.1:8000/reports/inventory/
- **Nhập/xuất**: http://127.0.0.1:8000/reports/import-export/
- **Lợi nhuận**: http://127.0.0.1:8000/reports/profit/

#### 4. Export Excel
- Test export báo cáo tồn kho
- Test export báo cáo nhập/xuất
- Test export báo cáo lợi nhuận

## Bước 5: Kiểm tra dữ liệu

### Kiểm tra database trực tiếp
```bash
python manage.py shell
```

Trong Django shell:
```python
from django.contrib.auth.models import User
from products.models import Product, Category
from inventory.models import Batch, Import, Export

# Kiểm tra users
User.objects.all()

# Kiểm tra sản phẩm
Product.objects.all()

# Kiểm tra lô hàng
Batch.objects.all()

# Kiểm tra phiếu nhập
Import.objects.all()

# Kiểm tra phiếu xuất
Export.objects.all()
```

## Troubleshooting

### Lỗi kết nối database
```bash
# Test kết nối
python test_db.py

# Kiểm tra DATABASE_URL
echo %DATABASE_URL%
```

### Lỗi migration
```bash
# Chạy migrations
python test_migrate.py
```

### Lỗi import dữ liệu
```bash
# Import lại dữ liệu
python import_data.py
```

### Lỗi static files
```bash
# Collect static files
python manage.py collectstatic
```

## Commands hữu ích

### Test nhanh
```bash
# Test database
python test_db.py

# Test app
python test_app.py

# Test migrate
python test_migrate.py

# Chạy local
python run_local.py
```

### Quản lý dữ liệu
```bash
# Backup dữ liệu
python scripts/export_sqlite_data.py

# Import dữ liệu
python import_data.py

# Tạo superuser
python create_superuser.py
```

## Lưu ý quan trọng

### Performance
- Database trên Render.com có thể chậm hơn local
- Kết nối internet ảnh hưởng đến tốc độ
- Nên test các chức năng chính trước

### Security
- Database credentials đã được expose trong code
- Chỉ dùng cho testing, không dùng production
- Thay đổi password sau khi test xong

### Backup
- Dữ liệu đã được backup trong thư mục `backup/`
- Có thể restore từ file JSON nếu cần

## Kết quả mong đợi

✅ **Kết nối database**: Thành công
✅ **Ứng dụng chạy**: http://127.0.0.1:8000/
✅ **Admin panel**: Truy cập được
✅ **Tất cả chức năng**: Hoạt động bình thường
✅ **Export Excel**: Thành công
✅ **Báo cáo**: Hiển thị đúng dữ liệu

## Bước tiếp theo

Sau khi test local thành công:
1. Deploy lên Render.com
2. Cấu hình domain
3. Setup SSL certificate
4. Monitor performance 