from django import forms
from .models import Import, ImportItem, Export, ExportItem, Batch
from products.models import Product, Category
import pandas as pd
from django.core.exceptions import ValidationError

class ImportForm(forms.ModelForm):
    """Form cho phiếu nhập kho"""
    class Meta:
        model = Import
        fields = ['supplier', 'notes']
        widgets = {
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ImportManualForm(forms.ModelForm):
    """Form cho phiếu nhập kho thủ công với nhiều sản phẩm"""
    
    class Meta:
        model = Import
        fields = ['supplier', 'notes']
        widgets = {
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ImportItemForm(forms.ModelForm):
    """Form cho từng item trong phiếu nhập kho"""
    
    # Thêm trường cho hạn sử dụng
    expiry_date = forms.DateField(
        required=True,
        label="Hạn sử dụng",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    class Meta:
        model = ImportItem
        fields = ['product', 'quantity', 'unit_price']
        labels = {
            'unit_price': 'Giá nhập',
        }
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Chỉ hiển thị tên sản phẩm trong dropdown
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        self.fields['product'].label_from_instance = lambda obj: obj.name
        
        # Set ngày mặc định cho hạn sử dụng (1 năm từ hôm nay)
        from django.utils import timezone
        default_date = timezone.now().date() + timezone.timedelta(days=365)
        self.fields['expiry_date'].initial = default_date

class ImportExcelForm(forms.Form):
    """Form import Excel cho phiếu nhập kho"""
    
    excel_file = forms.FileField(
        label="File Excel",
        help_text="Upload file Excel (.xlsx, .xls) với cấu trúc: Tên SP, Danh mục, Số lượng, Giá nhập, Giá bán, Đơn vị, Hạn sử dụng, Mô tả",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']
        
        # Kiểm tra định dạng file
        if not file.name.endswith(('.xlsx', '.xls')):
            raise ValidationError("Chỉ chấp nhận file Excel (.xlsx, .xls)")
        
        # Kiểm tra kích thước file (max 5MB)
        if file.size > 5 * 1024 * 1024:
            raise ValidationError("File quá lớn. Kích thước tối đa là 5MB.")
        
        try:
            # Đọc file Excel
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file, engine='openpyxl')
            else:
                df = pd.read_excel(file, engine='xlrd')
            
            # Kiểm tra cấu trúc cột
            required_columns = ['Tên SP', 'Danh mục', 'Số lượng', 'Giá nhập', 'Giá bán', 'Đơn vị']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValidationError(f"Thiếu các cột bắt buộc: {', '.join(missing_columns)}")
            
            # Kiểm tra dữ liệu
            if df.empty:
                raise ValidationError("File Excel không có dữ liệu")
            
            # Kiểm tra danh mục tồn tại (chỉ để thông báo, không bắt buộc)
            category_names = df['Danh mục'].dropna().astype(str)
            existing_categories = Category.objects.filter(name__in=category_names)
            existing_category_names = set(existing_categories.values_list('name', flat=True))
            
            missing_categories = set(category_names) - existing_category_names
            if missing_categories:
                # Lưu thông tin danh mục thiếu vào session để hiển thị cảnh báo
                if not hasattr(self, 'missing_categories'):
                    self.missing_categories = list(missing_categories)
            
            # Lưu DataFrame vào session để sử dụng sau
            self.excel_data = df
            
        except Exception as e:
            raise ValidationError(f"Lỗi khi đọc file Excel: {str(e)}")
        
        return file

class ImportItemBulkForm(forms.Form):
    """Form để xác nhận dữ liệu import từ Excel"""
    
    def __init__(self, excel_data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if excel_data is not None:
            self.excel_data = excel_data
            self._create_dynamic_fields()
    
    def _create_dynamic_fields(self):
        """Tạo các trường động từ dữ liệu Excel"""
        for index, row in enumerate(self.excel_data):
            product_name = str(row['Tên SP'])
            category_name = str(row['Danh mục'])
            quantity = row['Số lượng']
            import_price = row['Giá nhập']
            selling_price = row['Giá bán']
            unit = str(row['Đơn vị'])
            description = str(row.get('Mô tả', ''))
            
            # Tạo field cho số lượng
            self.fields[f'quantity_{index}'] = forms.IntegerField(
                initial=quantity,
                min_value=1,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
            
            # Tạo field cho giá nhập
            self.fields[f'import_price_{index}'] = forms.DecimalField(
                initial=import_price,
                min_value=0,
                decimal_places=2,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
            
            # Tạo field cho giá bán
            self.fields[f'selling_price_{index}'] = forms.DecimalField(
                initial=selling_price,
                min_value=0,
                decimal_places=2,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
            
            # Tạo field cho danh mục (dropdown hoặc text input)
            # Kiểm tra xem danh mục có tồn tại không
            existing_categories = Category.objects.all().order_by('name')
            category_exists = existing_categories.filter(name=category_name).exists()
            
            if category_exists:
                # Nếu danh mục tồn tại, sử dụng dropdown với giá trị mặc định
                self.fields[f'category_{index}'] = forms.ModelChoiceField(
                    queryset=existing_categories,
                    initial=existing_categories.filter(name=category_name).first(),
                    widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'style': 'width: 120px;'})
                )
            else:
                # Nếu danh mục không tồn tại, sử dụng dropdown với option "Tạo mới"
                choices = [('', '-- Chọn danh mục --')] + [(cat.id, cat.name) for cat in existing_categories] + [('new', f'Tạo mới: {category_name}')]
                self.fields[f'category_{index}'] = forms.ChoiceField(
                    choices=choices,
                    initial='',
                    widget=forms.Select(attrs={'class': 'form-control form-control-sm', 'style': 'width: 120px;'})
                )
            
            # Tạo field cho hạn sử dụng
            expiry_date = row.get('Hạn sử dụng', None)
            if expiry_date is None or (hasattr(expiry_date, 'isna') and expiry_date.isna()):
                from django.utils import timezone
                expiry_date = timezone.now().date() + timezone.timedelta(days=365)
            
            self.fields[f'expiry_date_{index}'] = forms.DateField(
                initial=expiry_date,
                widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
            )
            
            # Tạo field checkbox để chọn sản phẩm
            self.fields[f'include_{index}'] = forms.BooleanField(
                initial=True,
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )

class ImportItemFormSet(forms.BaseFormSet):
    """FormSet cho nhiều items"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

class ExportForm(forms.ModelForm):
    """Form cho phiếu xuất kho"""
    class Meta:
        model = Export
        fields = ['customer', 'notes']
        widgets = {
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExportItemForm(forms.ModelForm):
    """Form cho từng item trong phiếu xuất kho"""
    # Thêm field để chọn sản phẩm thay vì batch
    product = forms.ModelChoiceField(
        queryset=None,
        empty_label="Chọn sản phẩm...",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Sản phẩm"
    )
    
    class Meta:
        model = ExportItem
        fields = ['quantity', 'unit_price', 'discount_percent']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': 0.01}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Chỉ hiển thị các sản phẩm có tồn kho > 0
        from products.models import Product
        products_with_stock = []
        for product in Product.objects.filter(is_active=True):
            if product.total_stock > 0:
                products_with_stock.append(product)
        
        self.fields['product'].queryset = Product.objects.filter(id__in=[p.id for p in products_with_stock])
        
        # Tùy chỉnh cách hiển thị - chỉ hiển thị tên sản phẩm
        self.fields['product'].label_from_instance = lambda obj: obj.name
        
        # Set giá trị mặc định cho discount_percent
        self.fields['discount_percent'].initial = 0

class ExportItemFormSet(forms.BaseFormSet):
    """FormSet cho nhiều items xuất kho"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False

class NewProductForm(forms.ModelForm):
    """Form để tạo sản phẩm mới khi nhập kho"""
    from products.models import Product
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'unit', 'selling_price', 'expiry_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 0.01}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set giá trị mặc định cho expiry_date (1 năm từ hôm nay)
        if not self.instance.pk:
            from django.utils import timezone
            default_date = timezone.now().date() + timezone.timedelta(days=365)
            self.fields['expiry_date'].initial = default_date 