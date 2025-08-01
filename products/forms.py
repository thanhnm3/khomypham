from django import forms
from .models import Product, Category
from inventory.models import Batch

class ProductForm(forms.ModelForm):
    """Form tạo sản phẩm mới - với giá bán và giá nhập"""
    
    # Thêm field giá nhập
    import_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        label="Giá nhập",
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01})
    )
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'unit', 'selling_price', 'expiry_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set ngày mặc định cho hạn sử dụng (1 năm từ hôm nay)
        if not self.instance.pk:  # Chỉ khi tạo mới
            from django.utils import timezone
            default_date = timezone.now().date() + timezone.timedelta(days=365)
            self.fields['expiry_date'].initial = default_date

class ProductUpdateForm(forms.ModelForm):
    """Form cập nhật sản phẩm - chỉ thông tin cơ bản"""
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'unit', 'selling_price', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 