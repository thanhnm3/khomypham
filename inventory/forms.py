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
            
            # Chuyển đổi DataFrame thành dictionary để có thể serialize
            # Xử lý các cột ngày tháng và số để tránh lỗi JSON serialization
            excel_data_dict = []
            for index, row in df.iterrows():
                row_dict = {}
                for col in df.columns:
                    value = row[col]
                    
                    # Xử lý các loại dữ liệu khác nhau
                    if pd.isna(value):
                        row_dict[col] = None
                    elif isinstance(value, pd.Timestamp):
                        # Chuyển Timestamp thành string
                        row_dict[col] = value.strftime('%Y-%m-%d')
                    elif isinstance(value, (int, float)):
                        # Giữ nguyên số
                        row_dict[col] = value
                    else:
                        # Chuyển thành string
                        row_dict[col] = str(value)
                
                excel_data_dict.append(row_dict)
            
            # Lưu dữ liệu đã xử lý vào session
            self.excel_data = excel_data_dict
            
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
            
            # Kiểm tra và tạo field cho tên sản phẩm
            product_name_is_valid = product_name.strip() and len(product_name.strip()) <= 200
            if product_name_is_valid:
                self.fields[f'product_name_{index}'] = forms.CharField(
                    initial=product_name,
                    max_length=200,
                    widget=forms.TextInput(attrs={'class': 'form-control form-control-sm product-name-valid', 'style': 'width: 150px;'})
                )
            else:
                self.fields[f'product_name_{index}'] = forms.CharField(
                    initial=product_name,
                    max_length=200,
                    widget=forms.TextInput(attrs={'class': 'form-control form-control-sm product-name-invalid', 'style': 'width: 150px;'})
                )
            
            # Kiểm tra và tạo field cho số lượng
            try:
                quantity_valid = isinstance(quantity, (int, float)) and quantity > 0
                if quantity_valid:
                    self.fields[f'quantity_{index}'] = forms.IntegerField(
                        initial=quantity,
                        min_value=1,
                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm quantity-valid', 'style': 'width: 80px;'})
                    )
                else:
                    self.fields[f'quantity_{index}'] = forms.IntegerField(
                        initial=1,
                        min_value=1,
                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm quantity-invalid', 'style': 'width: 80px;'})
                    )
            except (ValueError, TypeError):
                self.fields[f'quantity_{index}'] = forms.IntegerField(
                    initial=1,
                    min_value=1,
                    widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm quantity-invalid', 'style': 'width: 80px;'})
                )
            
            # Kiểm tra và tạo field cho giá nhập
            try:
                import_price_valid = isinstance(import_price, (int, float)) and import_price >= 0
                if import_price_valid:
                    self.fields[f'import_price_{index}'] = forms.DecimalField(
                        initial=import_price,
                        min_value=0,
                        decimal_places=2,
                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm import-price-valid', 'style': 'width: 100px;'})
                    )
                else:
                    self.fields[f'import_price_{index}'] = forms.DecimalField(
                        initial=0,
                        min_value=0,
                        decimal_places=2,
                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm import-price-invalid', 'style': 'width: 100px;'})
                    )
            except (ValueError, TypeError):
                self.fields[f'import_price_{index}'] = forms.DecimalField(
                    initial=0,
                    min_value=0,
                    decimal_places=2,
                    widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm import-price-invalid', 'style': 'width: 100px;'})
                )
            
            # Kiểm tra và tạo field cho giá bán
            try:
                selling_price_valid = isinstance(selling_price, (int, float)) and selling_price >= 0
                if selling_price_valid:
                    self.fields[f'selling_price_{index}'] = forms.DecimalField(
                        initial=selling_price,
                        min_value=0,
                        decimal_places=2,
                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm selling-price-valid', 'style': 'width: 100px;'})
                    )
                else:
                    self.fields[f'selling_price_{index}'] = forms.DecimalField(
                        initial=0,
                        min_value=0,
                        decimal_places=2,
                        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm selling-price-invalid', 'style': 'width: 100px;'})
                    )
            except (ValueError, TypeError):
                self.fields[f'selling_price_{index}'] = forms.DecimalField(
                    initial=0,
                    min_value=0,
                    decimal_places=2,
                    widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm selling-price-invalid', 'style': 'width: 100px;'})
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
            
            # Tạo field cho đơn vị (có thể chỉnh sửa)
            unit = str(row['Đơn vị'])
            # Kiểm tra đơn vị hợp lệ (không rỗng và có độ dài hợp lý)
            unit_is_valid = unit.strip() and len(unit.strip()) <= 20
            
            if unit_is_valid:
                self.fields[f'unit_{index}'] = forms.CharField(
                    initial=unit,
                    max_length=20,
                    widget=forms.TextInput(attrs={'class': 'form-control form-control-sm unit-valid', 'style': 'width: 80px;'})
                )
            else:
                self.fields[f'unit_{index}'] = forms.CharField(
                    initial=unit,
                    max_length=20,
                    widget=forms.TextInput(attrs={'class': 'form-control form-control-sm unit-invalid', 'style': 'width: 80px;'})
                )
            
            # Tạo field cho hạn sử dụng (có thể chỉnh sửa)
            expiry_date = row.get('Hạn sử dụng', None)
            if expiry_date is None:
                from django.utils import timezone
                expiry_date = timezone.now().date() + timezone.timedelta(days=365)
                expiry_is_valid = False
            else:
                # Kiểm tra hạn sử dụng hợp lệ
                try:
                    if isinstance(expiry_date, str):
                        # Nếu là string, thử parse
                        from datetime import datetime
                        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                    elif hasattr(expiry_date, 'date'):
                        # Nếu là datetime object
                        expiry_date = expiry_date.date()
                    
                    # Kiểm tra hạn sử dụng không trong quá khứ
                    from django.utils import timezone
                    today = timezone.now().date()
                    expiry_is_valid = expiry_date >= today
                except:
                    # Nếu có lỗi parse, đặt ngày mặc định
                    from django.utils import timezone
                    expiry_date = timezone.now().date() + timezone.timedelta(days=365)
                    expiry_is_valid = False
            
            if expiry_is_valid:
                self.fields[f'expiry_date_{index}'] = forms.DateField(
                    initial=expiry_date,
                    widget=forms.DateInput(attrs={'class': 'form-control form-control-sm expiry-valid', 'type': 'date', 'style': 'width: 130px;'})
                )
            else:
                self.fields[f'expiry_date_{index}'] = forms.DateField(
                    initial=expiry_date,
                    widget=forms.DateInput(attrs={'class': 'form-control form-control-sm expiry-invalid', 'type': 'date', 'style': 'width: 130px;'})
                )
            
            # Tạo field checkbox để chọn sản phẩm
            self.fields[f'include_{index}'] = forms.BooleanField(
                initial=True,
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )
    
    def clean(self):
        """Validation cho form"""
        cleaned_data = super().clean()
        
        # Kiểm tra từng item được chọn
        for index, row in enumerate(self.excel_data):
            if cleaned_data.get(f'include_{index}', False):
                # Kiểm tra tên sản phẩm
                product_name = cleaned_data.get(f'product_name_{index}', '').strip()
                if not product_name:
                    self.add_error(f'product_name_{index}', 'Tên sản phẩm không được để trống')
                elif len(product_name) > 200:
                    self.add_error(f'product_name_{index}', 'Tên sản phẩm không được quá 200 ký tự')
                
                # Kiểm tra số lượng
                quantity = cleaned_data.get(f'quantity_{index}')
                if not quantity or quantity <= 0:
                    self.add_error(f'quantity_{index}', 'Số lượng phải lớn hơn 0')
                
                # Kiểm tra giá nhập
                import_price = cleaned_data.get(f'import_price_{index}')
                if import_price is None or import_price < 0:
                    self.add_error(f'import_price_{index}', 'Giá nhập không được âm')
                
                # Kiểm tra giá bán
                selling_price = cleaned_data.get(f'selling_price_{index}')
                if selling_price is None or selling_price < 0:
                    self.add_error(f'selling_price_{index}', 'Giá bán không được âm')
                
                # Kiểm tra đơn vị
                unit = cleaned_data.get(f'unit_{index}', '').strip()
                if not unit:
                    self.add_error(f'unit_{index}', 'Đơn vị không được để trống')
                elif len(unit) > 20:
                    self.add_error(f'unit_{index}', 'Đơn vị không được quá 20 ký tự')
                
                # Kiểm tra hạn sử dụng
                expiry_date = cleaned_data.get(f'expiry_date_{index}')
                if expiry_date:
                    from django.utils import timezone
                    today = timezone.now().date()
                    if expiry_date < today:
                        self.add_error(f'expiry_date_{index}', 'Hạn sử dụng không được trong quá khứ')
        
        return cleaned_data

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
        # Chỉ hiển thị các sản phẩm có tồn kho > 0 và loại bỏ trùng lặp theo tên
        from products.models import Product
        
        # Lấy sản phẩm có tồn kho > 0 và loại bỏ trùng lặp theo tên
        products_with_stock = []
        seen_names = set()
        
        for product in Product.objects.filter(is_active=True).order_by('name', 'id'):
            if product.name not in seen_names and product.total_stock > 0:
                products_with_stock.append(product)
                seen_names.add(product.name)
        
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