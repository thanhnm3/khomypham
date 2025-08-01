# 🚀 Hướng Dẫn Deploy Kho Mỹ Phẩm lên Render

## 📋 Yêu cầu trước khi deploy

1. **Tài khoản Render.com** - Đăng ký tại [render.com](https://render.com)
2. **Database PostgreSQL** - Đã có sẵn trên Render
3. **Git repository** - Code đã được push lên GitHub/GitLab

## 🔧 Cấu hình Deployment

### 1. File cấu hình chính

- **`render.yaml`** - Cấu hình service trên Render
- **`production_settings.py`** - Settings cho production
- **`requirements_production.txt`** - Dependencies cho production
- **`Procfile`** - Cấu hình process cho Render

### 2. Environment Variables

Trên Render Dashboard, thiết lập các biến môi trường:

```bash
DJANGO_SETTINGS_MODULE=kho_my_pham.production_settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=khomypham.onrender.com
DATABASE_URL=postgresql://khomypham_user:t07FMiBJ7dcCacUvydxBC4o9tSLTw1Hd@dpg-d24qrjili9vc73ej9sqg-a.singapore-postgres.render.com/khomypham
```

## 🚀 Các bước Deploy

### Bước 1: Test locally
```bash
python test_production_local.py
```

### Bước 2: Push code lên Git
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Bước 3: Deploy trên Render
1. Vào [Render Dashboard](https://dashboard.render.com)
2. Tạo New Web Service
3. Connect với Git repository
4. Cấu hình theo `render.yaml`
5. Deploy

### Bước 4: Kiểm tra deployment
```bash
python check_deployment.py
```

## 🔍 Kiểm tra sau khi deploy

### 1. Kiểm tra website
- URL: https://khomypham.onrender.com/
- Admin: https://khomypham.onrender.com/admin/

### 2. Kiểm tra logs
- Vào Render Dashboard > Service > Logs
- Kiểm tra build logs và runtime logs

### 3. Kiểm tra database
- Kết nối PostgreSQL
- Chạy migrations
- Tạo superuser nếu cần

## 🛠️ Scripts hữu ích

### Test production locally
```bash
python test_production_local.py
```

### Check deployment status
```bash
python check_deployment.py
```

### Deploy production
```bash
python deploy_production.py
```

### Clear database (cẩn thận!)
```bash
python clear_db_simple.py
```

## 🔧 Troubleshooting

### Lỗi thường gặp:

1. **Static files không load**
   - Kiểm tra `STATIC_ROOT` và `STATICFILES_STORAGE`
   - Chạy `collectstatic` trong build command

2. **Database connection failed**
   - Kiểm tra `DATABASE_URL`
   - Đảm bảo database đã được tạo

3. **Import errors**
   - Kiểm tra `requirements_production.txt`
   - Đảm bảo tất cả dependencies đã được cài đặt

4. **Settings module not found**
   - Kiểm tra `DJANGO_SETTINGS_MODULE`
   - Đảm bảo `production_settings.py` tồn tại

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra logs trên Render Dashboard
2. Chạy `check_deployment.py` để debug
3. Kiểm tra environment variables
4. Xem hướng dẫn chi tiết trong `DEPLOYMENT_GUIDE.md` 