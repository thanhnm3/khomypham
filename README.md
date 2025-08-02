# 🏪 Kho Mỹ Phẩm - Hệ thống quản lý kho

Hệ thống quản lý kho mỹ phẩm được xây dựng bằng Django với PostgreSQL database, hỗ trợ quản lý sản phẩm, nhập/xuất kho, báo cáo và export Excel.

## 📋 Tính năng chính

### 🛍️ Quản lý sản phẩm
- ✅ Thêm/sửa/xóa sản phẩm và danh mục
- ✅ Quản lý hình ảnh sản phẩm
- ✅ Theo dõi giá nhập và giá bán

### 📦 Quản lý kho
- ✅ Nhập kho với lô hàng và hạn sử dụng
- ✅ Xuất kho theo FIFO (First In, First Out)
- ✅ Cảnh báo sắp hết hàng và hết hạn
- ✅ Import/Export Excel

### 📊 Báo cáo và thống kê
- ✅ Báo cáo tồn kho theo danh mục
- ✅ Báo cáo nhập/xuất kho theo thời gian
- ✅ Báo cáo lợi nhuận
- ✅ Export Excel cho tất cả báo cáo

### 👥 Quản lý người dùng
- ✅ Phân quyền admin/staff
- ✅ Hồ sơ người dùng chi tiết

## 🛠️ Công nghệ sử dụng

- **Backend**: Django 5.2.4
- **Database**: PostgreSQL (Render.com)
- **Frontend**: Bootstrap 5, Crispy Forms
- **Deployment**: Render.com
- **File handling**: Pillow, OpenPyXL, Pandas
- **Static files**: WhiteNoise

## 🚀 Deployment

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=kho-my-pham.onrender.com
DATABASE_URL=postgresql://username:password@host:port/database
```

### Build Commands
```bash
pip install -r requirements_production.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

### Start Command
```bash
gunicorn kho_my_pham.wsgi:application
```

## 🔧 Development Setup

### 1. Clone repository
```bash
git clone <repository-url>
cd kho_my_pham
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình database
Tạo file `.env`:
```bash
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://username:password@host:port/database
```

### 4. Chạy migrations
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Chạy server
```bash
python manage.py runserver
```

## 📁 Cấu trúc dự án

```
kho_my_pham/
├── accounts/          # Quản lý người dùng
├── products/          # Quản lý sản phẩm
├── inventory/         # Quản lý kho
├── reports/           # Báo cáo
├── static/            # CSS, JS, Images
├── templates/         # HTML templates
├── kho_my_pham/       # Django settings
├── requirements.txt   # Dependencies local
├── requirements_production.txt  # Dependencies production
└── render.yaml        # Render.com config
```

## 📊 Database Schema

### Users & Profiles
- `auth_user`: Người dùng hệ thống
- `accounts_profile`: Hồ sơ người dùng

### Products
- `products_category`: Danh mục sản phẩm
- `products_product`: Thông tin sản phẩm

### Inventory
- `inventory_batch`: Lô hàng (quản lý hạn sử dụng)
- `inventory_import`: Phiếu nhập kho
- `inventory_importitem`: Chi tiết nhập kho
- `inventory_export`: Phiếu xuất kho
- `inventory_exportitem`: Chi tiết xuất kho

## 🧪 Testing

### Kiểm tra deployment
```bash
python check_deployment.py
```

### Test database connection
```bash
python test_db.py
```

### Test application
```bash
python test_app.py
```

### Chạy local với PostgreSQL
```bash
python run_local.py
```

## 🔒 Security

- ✅ HTTPS enabled
- ✅ XSS protection
- ✅ CSRF protection
- ✅ SQL injection protection
- ✅ Secure headers

## 📈 Performance

- **Database**: PostgreSQL trên Render.com
- **Static Files**: WhiteNoise compression
- **Caching**: Django ORM optimization
- **Security**: HTTPS, XSS protection

## 🚨 Troubleshooting

### Lỗi thường gặp:

1. **Database connection failed**
   - Kiểm tra DATABASE_URL
   - Đảm bảo database đã được tạo

2. **Static files not found**
   - Chạy `python manage.py collectstatic`
   - Kiểm tra STATIC_ROOT trong settings

3. **Import errors (pandas, etc.)**
   - Kiểm tra `requirements_production.txt`
   - Chạy `python check_deployment.py`

4. **Migration errors**
   - Kiểm tra database schema
   - Chạy `python manage.py migrate`

### Commands hữu ích:
```bash
# Test deployment
python check_deployment.py

# Test database
python test_db.py

# Test app
python test_app.py

# Clear database (cẩn thận!)
python clear_db_simple.py
```

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs trên Render Dashboard
2. Chạy `python check_deployment.py`
3. Kiểm tra environment variables
4. Xem logs trong terminal

## 📝 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

---

**Lưu ý**: Đây là phiên bản production-ready với PostgreSQL database. Để chạy local, hãy sử dụng SQLite hoặc cấu hình PostgreSQL local. 