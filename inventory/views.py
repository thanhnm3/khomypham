from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import Import, ImportItem, Batch, Export, ExportItem
from .forms import ImportForm, ImportItemForm, ImportExcelForm, ImportItemBulkForm, ImportItemFormSet, ExportForm, ExportItemForm, ExportItemFormSet, ImportManualForm
from products.models import Product, Category
import json
import io
import xlsxwriter

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
            
            # Cập nhật hạn sử dụng của sản phẩm nếu chưa có
            if not item.product.expiry_date and expiry_date:
                item.product.expiry_date = expiry_date
                item.product.save()
            
            # Tạo lô hàng
            batch = Batch.objects.create(
                product=item.product,
                import_date=import_order.import_date.date(),
                import_quantity=item.quantity,
                remaining_quantity=item.quantity,
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
            
            # Lưu thông tin danh mục thiếu nếu có
            if hasattr(form, 'missing_categories'):
                request.session['missing_categories'] = form.missing_categories
            
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
    missing_categories = request.session.get('missing_categories', [])
    
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
                    category_name = form.cleaned_data[f'category_{index}']  # Lấy từ form đã chỉnh sửa
                    quantity = form.cleaned_data[f'quantity_{index}']
                    import_price = form.cleaned_data[f'import_price_{index}']
                    selling_price = form.cleaned_data[f'selling_price_{index}']
                    unit = row['Đơn vị']
                    description = row.get('Mô tả', '')
                    expiry_date = form.cleaned_data[f'expiry_date_{index}']
                    
                    # Xử lý danh mục
                    category_value = form.cleaned_data[f'category_{index}']
                    
                    if category_value == 'new':
                        # Người dùng chọn tạo danh mục mới
                        category, category_created = Category.objects.get_or_create(
                            name=category_name
                        )
                    else:
                        # Người dùng chọn danh mục có sẵn
                        # category_value có thể là Category object hoặc ID string
                        if isinstance(category_value, Category):
                            category = category_value
                        else:
                            category = Category.objects.get(id=category_value)
                    
                    # Tìm hoặc tạo sản phẩm
                    product, created = Product.objects.get_or_create(
                        name=product_name,
                        category=category,
                        defaults={
                            'unit': unit,
                            'selling_price': selling_price,
                            'purchase_price': import_price,
                            'description': description,
                            'is_active': True
                        }
                    )
                    
                    # Cập nhật thông tin sản phẩm cũ
                    if not created:
                        # Cập nhật giá bán nếu có
                        if selling_price:
                            product.selling_price = selling_price
                        # Cập nhật giá nhập nếu chưa có
                        if not product.purchase_price and import_price:
                            product.purchase_price = import_price
                        # Cập nhật đơn vị nếu chưa có
                        if not product.unit:
                            product.unit = unit
                        # Cập nhật mô tả nếu chưa có
                        if not product.description and description:
                            product.description = description
                        product.save()
                    
                    # Tạo ImportItem
                    ImportItem.objects.create(
                        import_order=import_order,
                        product=product,
                        quantity=quantity,
                        unit_price=import_price
                    )
                    
                    # Cập nhật hạn sử dụng của sản phẩm nếu chưa có
                    if not product.expiry_date and expiry_date:
                        product.expiry_date = expiry_date
                        product.save()
                    
                    # Tạo lô hàng
                    Batch.objects.create(
                        product=product,
                        import_date=import_order.import_date.date(),
                        import_quantity=quantity,
                        remaining_quantity=quantity,
                        created_by=request.user
                    )
            
            # Xóa dữ liệu session
            del request.session['excel_data']
            if 'missing_categories' in request.session:
                del request.session['missing_categories']
            
            messages.success(request, f'Đã import thành công {import_order.items.count()} sản phẩm!')
            return redirect('inventory:import_detail', pk=import_order.pk)
    else:
        form = ImportItemBulkForm(excel_data=excel_data)
    
    context = {
        'form': form,
        'excel_data': excel_data,
        'missing_categories': missing_categories,
        'title': 'Xác nhận dữ liệu import',
    }
    return render(request, 'inventory/import_excel_confirm.html', context)

@login_required
def import_detail(request, pk):
    """Chi tiết phiếu nhập kho"""
    import_order = get_object_or_404(Import, pk=pk)
    items = import_order.items.all()
    
    # Thêm context cho ngày hết hạn
    from django.utils import timezone
    today = timezone.now().date()
    expiring_soon = today + timezone.timedelta(days=270)  # 9 tháng
    
    context = {
        'import_order': import_order,
        'items': items,
        'today': today,
        'expiring_soon': expiring_soon,
    }
    return render(request, 'inventory/import_detail.html', context)

@login_required
def import_update(request, pk):
    """Chỉnh sửa phiếu nhập kho"""
    import_order = get_object_or_404(Import, pk=pk)
    
    if request.method == 'POST':
        form = ImportManualForm(request.POST, instance=import_order)
        if form.is_valid():
            # Cập nhật thông tin phiếu nhập
            import_order = form.save()
            
            # Xử lý danh sách sản phẩm
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            purchase_prices = request.POST.getlist('purchase_prices[]')
            selling_prices = request.POST.getlist('selling_prices[]')
            
            # Lưu thông tin items trước khi xóa để xóa batches
            items_to_delete = list(import_order.items.all())
            
            # Xóa tất cả items cũ
            import_order.items.all().delete()
            
            # Xóa batches liên quan đến phiếu nhập này
            for item in items_to_delete:
                Batch.objects.filter(
                    product=item.product,
                    import_date=import_order.import_date.date(),
                    import_quantity=item.quantity
                ).delete()
            
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
                            import_quantity=quantity,
                            remaining_quantity=quantity,
                            created_by=request.user
                        )
                        
                        success_count += 1
                        
                    except (Product.DoesNotExist, ValueError) as e:
                        messages.error(request, f'Lỗi khi xử lý sản phẩm thứ {i+1}: {str(e)}')
            
            if success_count > 0:
                messages.success(request, f'Đã cập nhật phiếu nhập kho thành công với {success_count} sản phẩm!')
                return redirect('inventory:import_detail', pk=import_order.pk)
            else:
                messages.error(request, 'Không có sản phẩm nào được thêm vào phiếu nhập kho.')
                return redirect('inventory:import_update', pk=import_order.pk)
    else:
        form = ImportManualForm(instance=import_order)
    
    # Lấy danh sách sản phẩm và danh mục
    products = Product.objects.filter(is_active=True).order_by('name')
    categories = Category.objects.all().order_by('name')
    
    # Lấy items hiện tại để hiển thị trong form
    current_items = import_order.items.all()
    
    context = {
        'form': form,
        'products': products,
        'categories': categories,
        'import_order': import_order,
        'current_items': current_items,
        'title': 'Chỉnh sửa phiếu nhập kho',
    }
    return render(request, 'inventory/import_manual_form.html', context)

@login_required
def import_delete(request, pk):
    """Xóa phiếu nhập kho"""
    import_order = get_object_or_404(Import, pk=pk)
    
    if request.method == 'POST':
        # Xóa tất cả batches liên quan
        for item in import_order.items.all():
            Batch.objects.filter(
                product=item.product,
                import_date=import_order.import_date.date(),
                import_quantity=item.quantity
            ).delete()
        
        # Xóa phiếu nhập
        import_order.delete()
        messages.success(request, f'Đã xóa phiếu nhập kho {import_order.import_code} thành công!')
        return redirect('inventory:import_list')
    
    context = {
        'import_order': import_order,
    }
    return render(request, 'inventory/import_confirm_delete.html', context)

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

@login_required
def get_batch_info(request, batch_id):
    """Lấy thông tin lô hàng qua AJAX"""
    try:
        batch = Batch.objects.get(id=batch_id, is_active=True)
        product = batch.product
        
        return JsonResponse({
            'success': True,
            'product_name': product.name,
            'remaining_quantity': batch.remaining_quantity,
            'import_date': batch.import_date.strftime('%d/%m/%Y'),
            'import_price': float(batch.import_price) if batch.import_price else 0,
            'selling_price': float(product.selling_price) if product.selling_price else 0
        })
    except Batch.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lô hàng không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_product_info(request, product_id):
    """Lấy thông tin sản phẩm qua AJAX"""
    try:
        from products.models import Product
        product = Product.objects.get(id=product_id, is_active=True)
        
        return JsonResponse({
            'success': True,
            'product_name': product.name,
            'total_stock': product.total_stock,
            'selling_price': float(product.selling_price) if product.selling_price else 0,
            'unit': product.unit
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sản phẩm không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

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
        # Xử lý xóa item
        delete_item_id = request.POST.get('delete_item')
        if delete_item_id:
            try:
                item = ExportItem.objects.get(id=delete_item_id, export_order=export_order)
                
                # Hoàn trả số lượng về tất cả các batch của sản phẩm này
                # Tính toán lại số lượng cần hoàn trả cho từng batch
                product = item.batch.product
                remaining_quantity = item.quantity
                
                # Lấy tất cả các batch của sản phẩm này theo thứ tự import_date (FIFO)
                batches = product.batches.filter(is_active=True).order_by('import_date')
                
                for batch in batches:
                    if remaining_quantity <= 0:
                        break
                    
                    # Tính số lượng đã xuất từ batch này (dựa trên remaining_quantity hiện tại)
                    # Giả sử batch ban đầu có import_quantity, và remaining_quantity hiện tại
                    # Số lượng đã xuất = import_quantity - remaining_quantity
                    original_quantity = batch.import_quantity
                    current_remaining = batch.remaining_quantity
                    exported_from_batch = original_quantity - current_remaining
                    
                    if exported_from_batch > 0:
                        # Hoàn trả số lượng cho batch này
                        restore_quantity = min(remaining_quantity, exported_from_batch)
                        batch.remaining_quantity += restore_quantity
                        batch.save()
                        remaining_quantity -= restore_quantity
                        print(f"Restored {restore_quantity} to batch {batch.batch_code}")
                
                item.delete()
                messages.success(request, 'Đã xóa sản phẩm khỏi phiếu xuất')
                return redirect('inventory:export_add_items', pk=pk)
            except ExportItem.DoesNotExist:
                messages.error(request, 'Không tìm thấy sản phẩm cần xóa')
                return redirect('inventory:export_add_items', pk=pk)
        
        # Xử lý thêm item mới
        form = ExportItemForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            unit_price = form.cleaned_data['unit_price']
            discount_percent = form.cleaned_data.get('discount_percent', 0)
            
            # Kiểm tra tổng tồn kho của sản phẩm
            total_stock = product.total_stock
            if quantity > total_stock:
                messages.error(request, f'Số lượng xuất ({quantity}) vượt quá tồn kho ({total_stock})')
                return redirect('inventory:export_add_items', pk=pk)
            
            # Kiểm tra tổng tồn kho có đủ không
            total_available = sum(batch.remaining_quantity for batch in product.batches.filter(is_active=True, remaining_quantity__gt=0))
            
            if quantity > total_available:
                messages.error(request, f'Số lượng xuất ({quantity}) vượt quá tồn kho hiện có ({total_available})')
                return redirect('inventory:export_add_items', pk=pk)
            
            # Tìm batch có số lượng phù hợp để xuất (FIFO)
            remaining_quantity = quantity
            batches_to_update = []
            
            for batch in product.batches.filter(is_active=True, remaining_quantity__gt=0).order_by('import_date'):
                if remaining_quantity <= 0:
                    break
                    
                batch_quantity = min(remaining_quantity, batch.remaining_quantity)
                batches_to_update.append((batch, batch_quantity))
                remaining_quantity -= batch_quantity
            
            # Tạo một ExportItem duy nhất cho sản phẩm này
            # Sử dụng batch đầu tiên làm đại diện
            first_batch = batches_to_update[0][0]
            
            try:
                # Tạo ExportItem mà không trigger validation save() của model
                export_item = ExportItem(
                    export_order=export_order,
                    batch=first_batch,
                    quantity=quantity,  # Tổng số lượng cần xuất
                    unit_price=unit_price,
                    discount_percent=discount_percent
                )
                
                # Cập nhật số lượng tồn kho cho tất cả các batch được sử dụng TRƯỚC khi lưu ExportItem
                for batch, batch_quantity in batches_to_update:
                    batch.remaining_quantity -= batch_quantity
                    batch.save()
                    print(f"Updated batch {batch.batch_code}: remaining_quantity = {batch.remaining_quantity}")
                
                # Bây giờ lưu ExportItem (sau khi đã cập nhật remaining_quantity)
                export_item.save()
                print(f"Created ExportItem: {export_item}")
                    
            except Exception as e:
                print(f"Error creating ExportItem: {e}")
                messages.error(request, f'Lỗi khi tạo chi tiết xuất kho: {e}')
                return redirect('inventory:export_add_items', pk=pk)
            
            messages.success(request, f'Đã xuất {quantity} {product.unit} {product.name}')
            return redirect('inventory:export_add_items', pk=pk)
    else:
        form = ExportItemForm()
    
    # Lấy danh sách items đã thêm
    items = export_order.items.all()
    
    context = {
        'form': form,
        'export_order': export_order,
        'export_items': items,
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

@login_required
def export_update(request, pk):
    """Cập nhật phiếu xuất kho"""
    export_order = get_object_or_404(Export, pk=pk)
    
    if request.method == 'POST':
        form = ExportForm(request.POST, instance=export_order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Phiếu xuất kho đã được cập nhật thành công!')
            return redirect('inventory:export_detail', pk=export_order.pk)
    else:
        form = ExportForm(instance=export_order)
    
    context = {
        'form': form,
        'export_order': export_order,
        'title': f'Cập nhật phiếu xuất - {export_order.export_code}',
    }
    return render(request, 'inventory/export_form.html', context)

@login_required
def export_delete(request, pk):
    """Xóa phiếu xuất kho"""
    export_order = get_object_or_404(Export, pk=pk)
    
    if request.method == 'POST':
        # Hoàn trả số lượng về các batch
        for item in export_order.items.all():
            # Hoàn trả số lượng về tất cả các batch của sản phẩm này
            product = item.batch.product
            remaining_quantity = item.quantity
            
            # Lấy tất cả các batch của sản phẩm này theo thứ tự import_date (FIFO)
            batches = product.batches.filter(is_active=True).order_by('import_date')
            
            for batch in batches:
                if remaining_quantity <= 0:
                    break
                
                # Tính số lượng đã xuất từ batch này
                original_quantity = batch.import_quantity
                current_remaining = batch.remaining_quantity
                exported_from_batch = original_quantity - current_remaining
                
                if exported_from_batch > 0:
                    # Hoàn trả số lượng cho batch này
                    restore_quantity = min(remaining_quantity, exported_from_batch)
                    batch.remaining_quantity += restore_quantity
                    batch.save()
                    remaining_quantity -= restore_quantity
        
        # Xóa phiếu xuất
        export_order.delete()
        messages.success(request, 'Phiếu xuất kho đã được xóa thành công!')
        return redirect('inventory:export_list')
    
    context = {
        'export_order': export_order,
    }
    return render(request, 'inventory/export_confirm_delete.html', context)

@login_required
def download_excel_template(request):
    """Tải file mẫu Excel cho import"""
    # Tạo workbook trong memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Mẫu nhập kho')
    
    # Định dạng header
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4CAF50',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Định dạng cho dữ liệu mẫu
    data_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    # Định dạng cho số
    number_format = workbook.add_format({
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '#,##0'
    })
    
    # Định dạng cho ngày
    date_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'num_format': 'dd/mm/yyyy'
    })
    
    # Đặt độ rộng cột
    worksheet.set_column('A:A', 25)  # Tên SP
    worksheet.set_column('B:B', 15)  # Danh mục
    worksheet.set_column('C:C', 12)  # Số lượng
    worksheet.set_column('D:D', 15)  # Giá nhập
    worksheet.set_column('E:E', 15)  # Giá bán
    worksheet.set_column('F:F', 10)  # Đơn vị
    worksheet.set_column('G:G', 15)  # Hạn sử dụng
    worksheet.set_column('H:H', 30)  # Mô tả
    
    # Header
    headers = ['Tên SP', 'Danh mục', 'Số lượng', 'Giá nhập', 'Giá bán', 'Đơn vị', 'Hạn sử dụng', 'Mô tả']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Dữ liệu mẫu
    sample_data = [
        ['Serum Vitamin C', 'Serum', 50, 350000, 550000, 'chai', '2025-12-31', 'Serum làm sáng da'],
        ['Kem chống nắng SPF50', 'Kem chống nắng', 30, 280000, 420000, 'tuyp', '2025-10-31', 'Kem chống nắng cao cấp'],
        ['Sữa rửa mặt dịu nhẹ', 'Sữa rửa mặt', 100, 120000, 180000, 'chai', '2025-08-31', 'Sữa rửa mặt cho da nhạy cảm']
    ]
    
    for row, data in enumerate(sample_data, start=1):
        for col, value in enumerate(data):
            if col in [2, 3, 4]:  # Số lượng, Giá nhập, Giá bán
                worksheet.write(row, col, value, number_format)
            elif col == 6:  # Hạn sử dụng
                worksheet.write(row, col, value, date_format)
            else:
                worksheet.write(row, col, value, data_format)
    
    workbook.close()
    output.seek(0)
    
    # Tạo response
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="mau_nhap_kho.xlsx"'
    
    return response 