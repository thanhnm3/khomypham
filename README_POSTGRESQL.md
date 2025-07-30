# Hướng dẫn chuyển đổi sang PostgreSQL trên Render.com

## Tổng quan
Dự án kho mỹ phẩm hiện tại đang sử dụng SQLite database. Để deploy lên production với PostgreSQL trên Render.com, bạn cần thực hiện các bước sau:

## 1. Chuẩn bị PostgreSQL trên Render.com

### Tạo PostgreSQL Database trên Render:
1. Đăng nhập vào [Render.com](https://render.com)
2. Tạo "New PostgreSQL" service
3. Đặt tên database (ví dụ: `kho-my-pham-db`)
4. Chọn region gần nhất (ví dụ: Frankfurt)
5. Chọn plan phù hợp (Free tier hoặc paid plan)
6. Ghi lại thông tin kết nối:
   - **Database Name**: `kho_my_pham_db`
   - **Username**: `kho_my_pham_user`
   - **Password**: (sẽ được tạo tự động)
   - **Host**: `dpg-xxxxx-a.frankfurt-postgres.render.com`
   - **Port**: `5432`
   - **External Database URL**: `postgresql://username:password@host:port/database_name`

## 2. Cấu hình Environment Variables

### Tạo file .env trong thư mục gốc:
```bash
# Django Settings
SECRET_KEY=your-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,localhost,127.0.0.1

# Database Settings
DATABASE_URL=postgresql://kho_my_pham_user:your_password@dpg-xxxxx-a.frankfurt-postgres.render.com/kho_my_pham_db
```

## 3. Backup dữ liệu hiện tại

### Export dữ liệu từ SQLite:
```bash
cd kho_my_pham
python scripts/export_sqlite_data.py
```

File backup sẽ được tạo trong thư mục `backup/` với định dạng JSON.

## 4. Cài đặt dependencies mới

### Cập nhật requirements.txt:
```bash
pip install -r requirements.txt
```

Các package mới đã được thêm:
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `python-decouple==3.8` - Environment variables management
- `dj-database-url==2.1.0` - Parse DATABASE_URL

## 5. Migrate database

### Chạy migrations trên PostgreSQL:
```bash
# Đảm bảo DATABASE_URL đã được set
python scripts/migrate_to_postgresql.py
```

Hoặc chạy từng lệnh:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## 6. Import dữ liệu (tùy chọn)

### Nếu muốn import dữ liệu từ backup:
```bash
python manage.py shell
```

Trong Django shell:
```python
import json
from datetime import datetime
from django.contrib.auth.models import User
from products.models import Category, Product
from inventory.models import Batch, Import, ImportItem, Export, ExportItem
from accounts.models import Profile

# Load backup data
with open('backup/data_backup_YYYYMMDD_HHMMSS.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Import data theo thứ tự
# 1. Users
for user_data in data['users']:
    User.objects.get_or_create(
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

# 2. Categories
for cat_data in data['categories']:
    Category.objects.get_or_create(
        id=cat_data['id'],
        defaults={
            'name': cat_data['name'],
            'description': cat_data['description'],
            'created_at': datetime.fromisoformat(cat_data['created_at']),
            'updated_at': datetime.fromisoformat(cat_data['updated_at']),
        }
    )

# 3. Products
for prod_data in data['products']:
    Product.objects.get_or_create(
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

# Tiếp tục với các model khác...
```

## 7. Deploy lên Render.com

### Tạo Web Service trên Render:
1. Connect GitHub repository
2. Chọn "Web Service"
3. Cấu hình:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn kho_my_pham.wsgi:application`
   - **Environment Variables**: Thêm các biến từ file .env

### Environment Variables cần set:
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `DATABASE_URL`

## 8. Kiểm tra và test

### Kiểm tra kết nối database:
```bash
python manage.py dbshell
```

### Test ứng dụng:
- Truy cập admin panel
- Kiểm tra các chức năng chính
- Verify dữ liệu đã được migrate

## 9. Troubleshooting

### Lỗi thường gặp:

1. **Connection refused**:
   - Kiểm tra DATABASE_URL
   - Đảm bảo database đã được tạo trên Render

2. **Permission denied**:
   - Kiểm tra username/password
   - Đảm bảo user có quyền truy cập database

3. **Migration errors**:
   - Xóa migrations cũ và tạo lại
   - Kiểm tra model compatibility

4. **Static files not found**:
   - Chạy `python manage.py collectstatic`
   - Cấu hình STATIC_ROOT trong settings

## 10. Monitoring và Maintenance

### Backup định kỳ:
- Sử dụng pg_dump để backup PostgreSQL
- Lưu trữ backup an toàn

### Performance monitoring:
- Sử dụng Django Debug Toolbar (development)
- Monitor database performance trên Render dashboard

## Lưu ý quan trọng:
- **Không bao giờ commit file .env** vào Git
- **Backup dữ liệu thường xuyên**
- **Test kỹ trước khi deploy production**
- **Monitor performance và costs** 