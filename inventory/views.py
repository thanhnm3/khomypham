from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from .models import Import, ImportItem, Batch, Export, ExportItem
from .forms import ImportForm, ImportItemForm, ImportExcelForm, ImportItemBulkForm, ImportItemFormSet, ExportForm, ExportItemForm, ExportItemFormSet, ImportManualForm
from products.models import Product, Category
import json

@login_required
def import_list(request):
    """Danh sách phiếu nhập kho"""
    imports = Import.objects.all().order_by('-import_date')
    
    # Phân trang
    paginator = Paginator(imports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'inventory/import_list.html', context)

@login_required
def import_create(request):
    """Tạo phiếu nhập kho mới"""
    if request.method == 'POST':
        form = ImportForm(request.POST)
        if form.is_valid():
            import_order = form.save(commit=False)
            import_order.created_by = request.user
            import_order.save()
            
            # Chuyển đến trang thêm items
            messages.success(request, 'Phiếu nhập kho đã được tạo! Vui lòng thêm sản phẩm.')
            return redirect('inventory:import_add_items', pk=import_order.pk)
    else:
        form = ImportForm()
    
    context = {
        'form': form,
        'title': 'Tạo phiếu nhập kho mới',
    }
    return render(request, 'inventory/import_form.html', context)

@login_required
def import_manual_create(request):
    """Tạo phiếu nhập kho thủ công với nhiều sản phẩm"""
    if request.method == 'POST':
        form = ImportManualForm(request.POST)
        if form.is_valid():
            # Tạo phiếu nhập kho
            import_order = form.save(commit=False)
            import_order.created_by = request.user
            import_order.save()
            
            # Xử lý danh sách sản phẩm
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            purchase_prices = request.POST.getlist('purchase_prices[]')
            selling_prices = request.POST.getlist('selling_prices[]')
            
            success_count = 0
            for i in range(len(products)):
                if products[i] and quantities[i]:
                    try:
                        product = Product.objects.get(id=products[i])
                        quantity = int(quantities[i])
                        
                        # Sử dụng giá từ form hoặc từ sản phẩm
                        purchase_price = float(purchase_prices[i]) if purchase_prices[i] else (product.purchase_price or 0)
                        selling_price = float(selling_prices[i]) if selling_prices[i] else (product.selling_price or 0)
                        
                        # Cập nhật giá nhập và giá bán của sản phẩm nếu chưa có
                        if not product.purchase_price:
                            product.purchase_price = purchase_price
                        if not product.selling_price and selling_price:
                            product.selling_price = selling_price
                        product.save()
                        
                        # Tạo item nhập kho
                        item = ImportItem.objects.create(
                            import_order=import_order,
                            product=product,
                            quantity=quantity,
                            unit_price=purchase_price
                        )
                        
                        # Tạo lô hàng
                        batch = Batch.objects.create(
                            product=product,
                            import_date=import_order.import_date.date(),
                            import_price=purchase_price,
                            import_quantity=quantity,
                            remaining_quantity=quantity,
                            created_by=request.user
                        )
                        
                        success_count += 1
                        
                    except (Product.DoesNotExist, ValueError) as e:
                        messages.error(request, f'Lỗi khi xử lý sản phẩm thứ {i+1}: {str(e)}')
            
            if success_count > 0:
                messages.success(request, f'Đã tạo phiếu nhập kho thành công với {success_count} sản phẩm!')
                return redirect('inventory:import_detail', pk=import_order.pk)
            else:
                messages.error(request, 'Không có sản phẩm nào được thêm vào phiếu nhập kho.')
                import_order.delete()  # Xóa phiếu nhập nếu không có sản phẩm
                return redirect('inventory:import_list')
    else:
        form = ImportManualForm()
    
    # Lấy danh sách sản phẩm và danh mục
    products = Product.objects.filter(is_active=True).order_by('name')
    categories = Category.objects.all().order_by('name')
    
    context = {
        'form': form,
        'products': products,
        'categories': categories,
        'title': 'Tạo phiếu nhập kho thủ công',
    }
    return render(request, 'inventory/import_manual_form.html', context)

@login_required
def import_add_items(request, pk):
    """Thêm items vào phiếu nhập kho"""
    import_order = get_object_or_404(Import, pk=pk)
    
    if request.method == 'POST':
        form = ImportItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.import_order = import_order
            
            # Lấy hạn sử dụng từ form
            expiry_date = form.cleaned_data['expiry_date']
            
            # Tạo lô hàng
            batch = Batch.objects.create(
                product=item.product,
                import_date=import_order.import_date.date(),
                import_price=item.unit_price,
                import_quantity=item.quantity,
                remaining_quantity=item.quantity,
                expiry_date=expiry_date,
                created_by=request.user
            )
            
            item.save()
            messages.success(request, f'Đã thêm {item.quantity} {item.product.unit} {item.product.name}')
            return redirect('inventory:import_add_items', pk=pk)
    else:
        form = ImportItemForm()
    
    # Lấy danh sách items đã thêm
    items = import_order.items.all()
    
    context = {
        'form': form,
        'import_order': import_order,
        'items': items,
        'title': f'Thêm sản phẩm - {import_order.import_code}',
    }
    return render(request, 'inventory/import_add_items.html', context)

@login_required
def import_excel(request):
    """Import phiếu nhập kho từ Excel"""
    if request.method == 'POST':
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            # Lưu dữ liệu Excel vào session
            request.session['excel_data'] = form.excel_data.to_dict('records')
            
            messages.success(request, 'File Excel đã được upload thành công! Vui lòng xác nhận dữ liệu.')
            return redirect('inventory:import_excel_confirm')
    else:
        form = ImportExcelForm()
    
    context = {
        'form': form,
        'title': 'Import phiếu nhập kho từ Excel',
    }
    return render(request, 'inventory/import_excel.html', context)

@login_required
def import_excel_confirm(request):
    """Xác nhận dữ liệu import từ Excel"""
    excel_data = request.session.get('excel_data')
    
    if not excel_data:
        messages.error(request, 'Không có dữ liệu Excel để xác nhận.')
        return redirect('inventory:import_excel')
    
    if request.method == 'POST':
        form = ImportItemBulkForm(excel_data=excel_data, data=request.POST)
        if form.is_valid():
            # Tạo phiếu nhập kho
            import_order = Import.objects.create(
                import_date=timezone.now(),
                supplier=request.POST.get('supplier', ''),
                notes=request.POST.get('notes', ''),
                created_by=request.user
            )
            
            # Xử lý từng item
            for index, row in enumerate(excel_data):
                if form.cleaned_data.get(f'include_{index}', False):
                    product_name = row['Tên SP']
                    category_name = row['Danh mục']
                    quantity = form.cleaned_data[f'quantity_{index}']
                    import_price = form.cleaned_data[f'import_price_{index}']
                    selling_price = form.cleaned_data[f'selling_price_{index}']
                    unit = row['Đơn vị']
                    description = row.get('Mô tả', '')
                    expiry_date = form.cleaned_data[f'expiry_date_{index}']
                    
                    # Tìm hoặc tạo sản phẩm
                    category = Category.objects.get(name=category_name)
                    product, created = Product.objects.get_or_create(
                        name=product_name,
                        category=category,
                        defaults={
                            'unit': unit,
                            'selling_price': selling_price,
                            'description': description,
                            'is_active': True
                        }
                    )
                    
                    # Cập nhật giá bán nếu sản phẩm đã tồn tại
                    if not created:
                        product.selling_price = selling_price
                        product.save()
                    
                    # Tạo ImportItem
                    ImportItem.objects.create(
                        import_order=import_order,
                        product=product,
                        quantity=quantity,
                        unit_price=import_price
                    )
                    
                    # Tạo lô hàng
                    Batch.objects.create(
                        product=product,
                        import_date=import_order.import_date.date(),
                        import_price=import_price,
                        import_quantity=quantity,
                        remaining_quantity=quantity,
                        expiry_date=expiry_date,
                        created_by=request.user
                    )
            
            # Xóa dữ liệu session
            del request.session['excel_data']
            
            messages.success(request, f'Đã import thành công {import_order.items.count()} sản phẩm!')
            return redirect('inventory:import_detail', pk=import_order.pk)
    else:
        form = ImportItemBulkForm(excel_data=excel_data)
    
    context = {
        'form': form,
        'excel_data': excel_data,
        'title': 'Xác nhận dữ liệu import',
    }
    return render(request, 'inventory/import_excel_confirm.html', context)

@login_required
def import_detail(request, pk):
    """Chi tiết phiếu nhập kho"""
    import_order = get_object_or_404(Import, pk=pk)
    items = import_order.items.all()
    
    context = {
        'import_order': import_order,
        'items': items,
    }
    return render(request, 'inventory/import_detail.html', context)

# AJAX views
@login_required
def get_product_info(request):
    """Lấy thông tin sản phẩm qua AJAX"""
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                return JsonResponse({
                    'success': True,
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'selling_price': str(product.selling_price),
                        'unit': product.unit,
                        'category': product.category.name,
                    }
                })
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Sản phẩm không tồn tại'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Thiếu product_id'
            })
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def create_product_ajax(request):
    """Tạo sản phẩm mới qua AJAX"""
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            unit = request.POST.get('unit')
            purchase_price = request.POST.get('purchase_price')
            selling_price = request.POST.get('selling_price')
            expiry_date = request.POST.get('expiry_date')
            description = request.POST.get('description', '')
            
            # Validate dữ liệu
            if not all([name, category_id, unit, purchase_price, selling_price, expiry_date]):
                return JsonResponse({
                    'success': False,
                    'errors': 'Vui lòng điền đầy đủ thông tin bắt buộc'
                })
            
            # Lấy category
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'errors': 'Danh mục không tồn tại'
                })
            
            # Tạo sản phẩm mới
            product = Product.objects.create(
                name=name,
                category=category,
                unit=unit,
                purchase_price=purchase_price,
                selling_price=selling_price,
                expiry_date=expiry_date,
                description=description,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'purchase_price': str(product.purchase_price) if product.purchase_price else '',
                    'selling_price': str(product.selling_price) if product.selling_price else '',
                    'unit': product.unit,
                    'category': product.category.name,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'errors': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Export views (giữ nguyên)
@login_required
def export_list(request):
    """Danh sách phiếu xuất kho"""
    exports = Export.objects.all().order_by('-export_date')
    
    # Phân trang
    paginator = Paginator(exports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'inventory/export_list.html', context)

@login_required
def export_create(request):
    """Tạo phiếu xuất kho mới"""
    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            export_order = form.save(commit=False)
            export_order.created_by = request.user
            export_order.save()
            
            messages.success(request, 'Phiếu xuất kho đã được tạo! Vui lòng thêm sản phẩm.')
            return redirect('inventory:export_add_items', pk=export_order.pk)
    else:
        form = ExportForm()
    
    context = {
        'form': form,
        'title': 'Tạo phiếu xuất kho mới',
    }
    return render(request, 'inventory/export_form.html', context)

@login_required
def export_add_items(request, pk):
    """Thêm items vào phiếu xuất kho"""
    export_order = get_object_or_404(Export, pk=pk)
    
    if request.method == 'POST':
        form = ExportItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.export_order = export_order
            
            # Kiểm tra số lượng tồn kho
            if item.quantity > item.batch.remaining_quantity:
                messages.error(request, f'Số lượng xuất vượt quá tồn kho ({item.batch.remaining_quantity})')
                return redirect('inventory:export_add_items', pk=pk)
            
            # Cập nhật số lượng tồn kho
            item.batch.remaining_quantity -= item.quantity
            item.batch.save()
            
            item.save()
            messages.success(request, f'Đã xuất {item.quantity} {item.batch.product.unit} {item.batch.product.name}')
            return redirect('inventory:export_add_items', pk=pk)
    else:
        form = ExportItemForm()
    
    # Lấy danh sách items đã thêm
    items = export_order.items.all()
    
    context = {
        'form': form,
        'export_order': export_order,
        'items': items,
        'title': f'Thêm sản phẩm - {export_order.export_code}',
    }
    return render(request, 'inventory/export_add_items.html', context)

@login_required
def export_detail(request, pk):
    """Chi tiết phiếu xuất kho"""
    export_order = get_object_or_404(Export, pk=pk)
    items = export_order.items.all()
    
    context = {
        'export_order': export_order,
        'items': items,
    }
    return render(request, 'inventory/export_detail.html', context) 