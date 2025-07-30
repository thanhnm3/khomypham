# Kho Mỹ Phẩm - Hệ thống quản lý kho

Hệ thống quản lý kho mỹ phẩm được xây dựng bằng Django với PostgreSQL database.

## 🚀 Live Demo

**Production URL**: https://kho-my-pham.onrender.com

**Admin Login**:
- Username: `admin`
- Password: `admin123`

## 📋 Tính năng

### Quản lý sản phẩm
- ✅ Thêm/sửa/xóa sản phẩm
- ✅ Phân loại theo danh mục
- ✅ Quản lý hình ảnh sản phẩm

### Quản lý kho
- ✅ Nhập kho với lô hàng
- ✅ Xuất kho theo FIFO
- ✅ Theo dõi hạn sử dụng
- ✅ Cảnh báo sắp hết hàng

### Báo cáo
- ✅ Báo cáo tồn kho
- ✅ Báo cáo nhập/xuất
- ✅ Báo cáo lợi nhuận
- ✅ Export Excel

### Quản lý người dùng
- ✅ Phân quyền admin/staff
- ✅ Hồ sơ người dùng

## 🛠️ Công nghệ

- **Backend**: Django 5.2.4
- **Database**: PostgreSQL (Render.com)
- **Frontend**: Bootstrap 5, Crispy Forms
- **Deployment**: Render.com
- **File handling**: Pillow, OpenPyXL

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

## 📁 Project Structure

```
kho_my_pham/
├── accounts/          # Quản lý người dùng
├── products/          # Quản lý sản phẩm
├── inventory/         # Quản lý kho
├── reports/           # Báo cáo
├── static/            # CSS, JS, Images
├── templates/         # HTML templates
├── scripts/           # Utility scripts
└── kho_my_pham/       # Django settings
```

## 🔧 Development

### Local Setup
```bash
# Clone repository
git clone <repository-url>
cd kho_my_pham

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://...

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Test Commands
```bash
# Test database connection
python test_db.py

# Test application
python test_app.py

# Fix sequences (if needed)
python fix_sequences.py
```

## 📈 Performance

- **Database**: PostgreSQL trên Render.com
- **Static Files**: WhiteNoise compression
- **Caching**: Django ORM optimization
- **Security**: HTTPS, XSS protection

## 🔒 Security

- ✅ HTTPS enabled
- ✅ XSS protection
- ✅ CSRF protection
- ✅ SQL injection protection
- ✅ Secure headers

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. Render.com logs
2. Database connection
3. Environment variables
4. Static files configuration

## 📝 License

MIT License - Xem file LICENSE để biết thêm chi tiết. 