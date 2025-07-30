from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from inventory.models import Batch, Import, Export, ExportItem
from django.utils import timezone
import json

@login_required
def dashboard(request):
    # Tổng quan
    total_products = Product.objects.filter(is_active=True).count()
    total_stock_value = sum(product.total_stock for product in Product.objects.filter(is_active=True))
    
    # Sản phẩm sắp hết hạn
    expiring_products = []
    for product in Product.objects.filter(is_active=True):
        expiring_batches = product.expiring_batches
        if expiring_batches.exists():
            expiring_products.append({
                'product': product,
                'batches': expiring_batches[:3]
            })
    
    # Sản phẩm sắp hết hàng
    low_stock_products = []
    for product in Product.objects.filter(is_active=True):
        low_stock_batches = product.low_stock_batches
        if low_stock_batches.exists():
            low_stock_products.append({
                'product': product,
                'batches': low_stock_batches[:3]
            })

    # Tồn kho theo danh mục (bar chart)
    categories = Category.objects.all()
    category_labels = [cat.name for cat in categories]
    category_stock = []
    for cat in categories:
        total = sum(p.total_stock for p in cat.product_set.filter(is_active=True))
        category_stock.append(total)

    # Sản phẩm tồn kho thấp nhất (top 5)
    products_with_stock = []
    for product in Product.objects.filter(is_active=True):
        products_with_stock.append({
            'name': product.name,
            'total_stock': product.total_stock
        })
    # Sắp xếp theo tồn kho tăng dần và lấy top 5
    products_with_stock.sort(key=lambda x: x['total_stock'])
    low_stock_list = products_with_stock[:5]
    low_stock_names = [p['name'] for p in low_stock_list]
    low_stock_values = [p['total_stock'] for p in low_stock_list]

    # Sản phẩm bán chạy nhất (top 5 theo số lượng xuất)
    top_export = (
        ExportItem.objects.values('batch__product__name')
        .annotate(total_export=Sum('quantity'))
        .order_by('-total_export')[:5]
    )
    top_export_names = [item['batch__product__name'] for item in top_export]
    top_export_values = [item['total_export'] for item in top_export]

    # Nhập/xuất theo ngày (7 ngày gần nhất)
    today = timezone.now().date()
    date_labels = [(today - timezone.timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)]
    import_data = []
    export_data = []
    for i in range(6, -1, -1):
        day = today - timezone.timedelta(days=i)
        import_data.append(
            Import.objects.filter(import_date__date=day).aggregate(Sum('items__quantity'))['items__quantity__sum'] or 0
        )
        export_data.append(
            Export.objects.filter(export_date__date=day).aggregate(Sum('items__quantity'))['items__quantity__sum'] or 0
        )

    context = {
        'total_products': total_products,
        'total_stock_value': total_stock_value,
        'expiring_products': expiring_products[:3],
        'low_stock_products': low_stock_products[:3],
        # Dashboard chart data
        'category_labels': json.dumps(category_labels, ensure_ascii=False),
        'category_stock': json.dumps(category_stock),
        'low_stock_names': json.dumps(low_stock_names, ensure_ascii=False),
        'low_stock_values': json.dumps(low_stock_values),
        'top_export_names': json.dumps(top_export_names, ensure_ascii=False),
        'top_export_values': json.dumps(top_export_values),
        'date_labels': json.dumps(date_labels),
        'import_data': json.dumps(import_data),
        'export_data': json.dumps(export_data),
    }
    return render(request, 'products/dashboard.html', context)

@login_required
def product_list(request):
    """Danh sách sản phẩm"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    products = Product.objects.filter(is_active=True)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    # Phân trang
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'products/product_list.html', context)

@login_required
def product_detail(request, pk):
    """Chi tiết sản phẩm"""
    product = get_object_or_404(Product, pk=pk)
    batches = product.batches.filter(is_active=True).order_by('expiry_date')
    
    context = {
        'product': product,
        'batches': batches,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def product_create(request):
    """Tạo sản phẩm mới"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được tạo thành công!')
            return redirect('products:product_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Thêm sản phẩm mới',
    }
    return render(request, 'products/product_form.html', context)

@login_required
def product_update(request, pk):
    """Cập nhật sản phẩm"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sản phẩm đã được cập nhật thành công!')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': 'Cập nhật sản phẩm',
    }
    return render(request, 'products/product_form.html', context)

@login_required
def product_delete(request, pk):
    """Xóa sản phẩm"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, 'Sản phẩm đã được xóa thành công!')
        return redirect('products:product_list')
    
    context = {
        'product': product,
    }
    return render(request, 'products/product_confirm_delete.html', context)

# Category views
@login_required
def category_list(request):
    """Danh sách danh mục"""
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'products/category_list.html', context)

@login_required
def category_create(request):
    """Tạo danh mục mới"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Danh mục đã được tạo thành công!')
            return redirect('products:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Thêm danh mục mới',
    }
    return render(request, 'products/category_form.html', context) 