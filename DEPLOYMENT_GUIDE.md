# Hướng dẫn Deployment lên Render.com

## Tóm tắt
Dự án kho mỹ phẩm đã được chuyển đổi thành công từ SQLite sang PostgreSQL trên Render.com.

## Thông tin Database hiện tại
- **Host**: `dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com`
- **Database**: `khomypham`
- **Username**: `khomypham_user`
- **Port**: `5432`
- **DATABASE_URL**: `postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham`

## Dữ liệu đã được migrate
✅ **Users**: 3 users (admin, hong, thanh)
✅ **Categories**: 9 categories (Botox, Filler, Kem chống nắng, etc.)
✅ **Products**: 3 products
✅ **Batches**: 2 batches
✅ **Imports**: 2 import orders
✅ **Exports**: 1 export order
✅ **Profiles**: 3 user profiles

## Bước tiếp theo để deploy lên Render.com

### 1. Tạo Web Service trên Render.com
1. Đăng nhập vào [Render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Cấu hình:
   - **Name**: `kho-my-pham`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements_production.txt`
   - **Start Command**: `gunicorn kho_my_pham.wsgi:application`

### 2. Environment Variables
Thêm các biến môi trường sau:

```
SECRET_KEY=django-insecure-u8&78e%ch+w(7#8a2nm)!$)+iihrx7h35e5pi-exh1z_w$=6se
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,localhost,127.0.0.1
DATABASE_URL=postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham
```

### 3. Cấu hình Static Files
Thêm vào `settings.py`:
```python
# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add whitenoise middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    # ... other middleware
]
```

### 4. Deploy
1. Commit và push code lên GitHub
2. Render sẽ tự động build và deploy
3. Kiểm tra logs nếu có lỗi

## Kiểm tra sau khi deploy

### 1. Test kết nối database
```bash
python manage.py check --database default
```

### 2. Test ứng dụng
- Truy cập: `https://your-app-name.onrender.com`
- Đăng nhập với:
  - Username: `admin`
  - Password: `admin123`

### 3. Kiểm tra các chức năng
- ✅ Quản lý sản phẩm
- ✅ Quản lý nhập/xuất kho
- ✅ Báo cáo tồn kho
- ✅ Báo cáo lợi nhuận
- ✅ Export Excel

## Backup và Maintenance

### Backup database
```bash
# Sử dụng pg_dump (nếu có)
pg_dump postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham > backup.sql
```

### Monitoring
- Kiểm tra logs trên Render dashboard
- Monitor database performance
- Backup dữ liệu định kỳ

## Troubleshooting

### Lỗi thường gặp:
1. **Database connection failed**: Kiểm tra DATABASE_URL
2. **Static files not found**: Chạy `python manage.py collectstatic`
3. **Migration errors**: Kiểm tra database schema
4. **Import errors**: Kiểm tra dependencies

### Commands hữu ích:
```bash
# Test database connection
python test_db.py

# Run migrations
python test_migrate.py

# Import data
python import_data.py

# Test application
python test_app.py
```

## Lưu ý quan trọng
- ✅ Database đã được migrate thành công
- ✅ Dữ liệu đã được import
- ✅ Ứng dụng hoạt động bình thường
- ⚠️ Cần deploy lên Render.com để có thể truy cập từ internet
- ⚠️ Cần cấu hình domain và SSL nếu cần

## Liên hệ hỗ trợ
Nếu gặp vấn đề, kiểm tra:
1. Render.com logs
2. Database connection
3. Environment variables
4. Static files configuration 