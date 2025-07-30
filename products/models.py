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
        ('cai', 'Cái'),
        ('hop', 'Hộp'),
        ('chai', 'Chai'),
        ('tuyp', 'Tuýp'),
        ('goi', 'Gói'),
        ('kg', 'Kg'),
        ('g', 'G'),
        ('ml', 'Ml'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Mã sản phẩm")
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Danh mục")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Hình ảnh")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='cai', verbose_name="Đơn vị tính")
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

    @property
    def total_stock(self):
        """Tổng tồn kho của sản phẩm"""
        return sum(batch.remaining_quantity for batch in self.batches.filter(is_active=True))

    @property
    def low_stock_batches(self):
        """Các lô hàng sắp hết"""
        return self.batches.filter(is_active=True, remaining_quantity__lte=10)

    @property
    def expiring_batches(self):
        """Các lô hàng sắp hết hạn (30 ngày)"""
        thirty_days_from_now = timezone.now().date() + timezone.timedelta(days=30)
        return self.batches.filter(is_active=True, expiry_date__lte=thirty_days_from_now) 