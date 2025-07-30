from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product

class Batch(models.Model):
    """Lô hàng - mỗi lần nhập kho tạo một lô mới"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches', verbose_name="Sản phẩm")
    batch_code = models.CharField(max_length=100, unique=True, verbose_name="Mã lô")
    import_date = models.DateField(verbose_name="Ngày nhập")
    expiry_date = models.DateField(verbose_name="Hạn sử dụng")
    import_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá nhập")
    import_quantity = models.IntegerField(verbose_name="Số lượng nhập")
    remaining_quantity = models.IntegerField(verbose_name="Số lượng còn lại")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lô hàng"
        verbose_name_plural = "Lô hàng"
        ordering = ['-import_date']

    def __str__(self):
        return f"{self.batch_code} - {self.product.name}"

    @property
    def is_expired(self):
        """Kiểm tra lô hàng đã hết hạn chưa"""
        return self.expiry_date < timezone.now().date()

    @property
    def is_expiring_soon(self):
        """Kiểm tra lô hàng sắp hết hạn (30 ngày)"""
        thirty_days_from_now = timezone.now().date() + timezone.timedelta(days=30)
        return self.expiry_date <= thirty_days_from_now

    @property
    def is_low_stock(self):
        """Kiểm tra lô hàng sắp hết"""
        return self.remaining_quantity <= 10

class Import(models.Model):
    """Phiếu nhập kho"""
    import_code = models.CharField(max_length=50, unique=True, verbose_name="Mã phiếu nhập")
    import_date = models.DateTimeField(default=timezone.now, verbose_name="Ngày nhập")
    supplier = models.CharField(max_length=200, blank=True, verbose_name="Nhà cung cấp")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phiếu nhập kho"
        verbose_name_plural = "Phiếu nhập kho"
        ordering = ['-import_date']

    def __str__(self):
        return f"PN{self.import_code} - {self.import_date.strftime('%d/%m/%Y')}"

    @property
    def total_amount(self):
        """Tổng giá trị phiếu nhập"""
        return sum(item.total_price for item in self.items.all())

class ImportItem(models.Model):
    """Chi tiết phiếu nhập kho"""
    import_order = models.ForeignKey(Import, on_delete=models.CASCADE, related_name='items', verbose_name="Phiếu nhập")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    batch_code = models.CharField(max_length=100, verbose_name="Mã lô")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Đơn giá")
    expiry_date = models.DateField(verbose_name="Hạn sử dụng")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi tiết nhập kho"
        verbose_name_plural = "Chi tiết nhập kho"

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.unit}"

    @property
    def total_price(self):
        """Tổng giá trị của item"""
        return self.quantity * self.unit_price

class Export(models.Model):
    """Phiếu xuất kho"""
    export_code = models.CharField(max_length=50, unique=True, verbose_name="Mã phiếu xuất")
    export_date = models.DateTimeField(default=timezone.now, verbose_name="Ngày xuất")
    customer = models.CharField(max_length=200, blank=True, verbose_name="Khách hàng")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người tạo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phiếu xuất kho"
        verbose_name_plural = "Phiếu xuất kho"
        ordering = ['-export_date']

    def __str__(self):
        return f"PX{self.export_code} - {self.export_date.strftime('%d/%m/%Y')}"

    @property
    def total_amount(self):
        """Tổng giá trị phiếu xuất"""
        return sum(item.total_price for item in self.items.all())

class ExportItem(models.Model):
    """Chi tiết phiếu xuất kho"""
    export_order = models.ForeignKey(Export, on_delete=models.CASCADE, related_name='items', verbose_name="Phiếu xuất")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, verbose_name="Lô hàng")
    quantity = models.IntegerField(verbose_name="Số lượng")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Đơn giá")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi tiết xuất kho"
        verbose_name_plural = "Chi tiết xuất kho"

    def __str__(self):
        return f"{self.batch.product.name} - {self.quantity} {self.batch.product.unit}"

    @property
    def total_price(self):
        """Tổng giá trị của item"""
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        """Cập nhật số lượng còn lại của lô hàng khi xuất"""
        if not self.pk:  # Chỉ khi tạo mới
            if self.quantity > self.batch.remaining_quantity:
                raise ValueError("Số lượng xuất không được vượt quá số lượng còn lại")
            self.batch.remaining_quantity -= self.quantity
            self.batch.save()
        super().save(*args, **kwargs) 