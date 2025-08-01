from django.db import models
from django.urls import reverse
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    UNIT_CHOICES = [
        ('hop', 'Hộp'),
        ('chai', 'Chai'),
        ('tuyp', 'Tuýp'),
        ('goi', 'Gói'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Mã sản phẩm", blank=True)
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Danh mục")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Hình ảnh")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='hop', verbose_name="Đơn vị tính")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá mua", null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá bán", null=True, blank=True)
    expiry_date = models.DateField(verbose_name="Hạn sử dụng", null=True, blank=True)
    expiry_days = models.IntegerField(verbose_name="Số ngày hết hạn", null=True, blank=True, default=365)
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # Tự động tạo mã sản phẩm nếu chưa có
        if not self.code:
            self.code = self.generate_product_code()
        super().save(*args, **kwargs)

    def generate_product_code(self):
        """Tự động tạo mã sản phẩm"""
        import datetime
        
        # Lấy prefix từ tên danh mục (3 ký tự đầu)
        category_prefix = self.category.name[:3].upper() if self.category else "SP"
        
        # Lấy năm hiện tại
        current_year = datetime.datetime.now().year
        
        # Tìm số thứ tự tiếp theo trong năm
        existing_products = Product.objects.filter(
            code__startswith=f"{category_prefix}{current_year}"
        ).count()
        
        # Tạo mã mới: CATEGORY + YEAR + SEQUENCE (3 chữ số)
        sequence = existing_products + 1
        return f"{category_prefix}{current_year}{sequence:03d}"

    @property
    def total_stock(self):
        """Tổng tồn kho của sản phẩm"""
        return sum(batch.remaining_quantity for batch in self.batches.filter(is_active=True))

    @property
    def low_stock_batches(self):
        """Các lô hàng sắp hết (tồn kho <= 1)"""
        return self.batches.filter(is_active=True, remaining_quantity__lte=1)

    @property
    def expiring_batches(self):
        """Các lô hàng sắp hết hạn (9 tháng)"""
        nine_months_from_now = timezone.now().date() + timezone.timedelta(days=270)  # 9 tháng = 270 ngày
        # Lọc các lô hàng có hạn sử dụng sắp hết
        expiring_batches = []
        for batch in self.batches.filter(is_active=True):
            if batch.expiry_date and batch.expiry_date <= nine_months_from_now:
                expiring_batches.append(batch)
        return expiring_batches

    @property
    def average_import_price(self):
        """Giá nhập trung bình của sản phẩm (sử dụng giá mua từ sản phẩm)"""
        return self.purchase_price or 0 