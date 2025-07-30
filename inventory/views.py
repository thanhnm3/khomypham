from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Import, Export, ImportItem, ExportItem, Batch
from products.models import Product
import uuid

@login_required
def import_list(request):
    """Danh sách phiếu nhập kho"""
    imports = Import.objects.all().order_by('-import_date')
    context = {
        'imports': imports,
    }
    return render(request, 'inventory/import_list.html', context)

@login_required
def import_create(request):
    """Tạo phiếu nhập kho"""
    if request.method == 'POST':
        # Tạo phiếu nhập
        import_code = f"PN{timezone.now().strftime('%Y%m%d%H%M%S')}"
        import_order = Import.objects.create(
            import_code=import_code,
            supplier=request.POST.get('supplier', ''),
            notes=request.POST.get('notes', ''),
            created_by=request.user
        )
        
        # Tạo chi tiết phiếu nhập
        product_id = request.POST.get('product')
        batch_code = request.POST.get('batch_code')
        quantity = int(request.POST.get('quantity'))
        unit_price = float(request.POST.get('unit_price'))
        expiry_date = request.POST.get('expiry_date')
        
        if product_id and batch_code and quantity and unit_price and expiry_date:
            product = Product.objects.get(id=product_id)
            
            # Tạo lô hàng mới
            batch = Batch.objects.create(
                product=product,
                batch_code=batch_code,
                import_date=timezone.now().date(),
                expiry_date=expiry_date,
                import_price=unit_price,
                import_quantity=quantity,
                remaining_quantity=quantity,
                created_by=request.user
            )
            
            # Tạo ImportItem để liên kết với Import
            ImportItem.objects.create(
                import_order=import_order,
                product=product,
                batch_code=batch_code,
                quantity=quantity,
                unit_price=unit_price,
                expiry_date=expiry_date
            )
            
            messages.success(request, 'Phiếu nhập kho đã được tạo thành công!')
            return redirect('inventory:import_list')
    
    products = Product.objects.filter(is_active=True)
    context = {
        'products': products,
    }
    return render(request, 'inventory/import_form.html', context)

@login_required
def export_list(request):
    """Danh sách phiếu xuất kho"""
    exports = Export.objects.all().order_by('-export_date')
    context = {
        'exports': exports,
    }
    return render(request, 'inventory/export_list.html', context)

@login_required
def export_create(request):
    """Tạo phiếu xuất kho"""
    if request.method == 'POST':
        # Tạo phiếu xuất
        export_code = f"PX{timezone.now().strftime('%Y%m%d%H%M%S')}"
        export_order = Export.objects.create(
            export_code=export_code,
            customer=request.POST.get('customer', ''),
            notes=request.POST.get('notes', ''),
            created_by=request.user
        )
        
        # Tạo chi tiết phiếu xuất
        batch_id = request.POST.get('batch')
        quantity = int(request.POST.get('quantity'))
        unit_price = float(request.POST.get('unit_price'))
        
        if batch_id and quantity and unit_price:
            batch = Batch.objects.get(id=batch_id)
            
            # Kiểm tra số lượng còn lại
            if quantity > batch.remaining_quantity:
                messages.error(request, 'Số lượng xuất vượt quá số lượng còn lại!')
                export_order.delete()
                return redirect('inventory:export_create')
            
            # Tạo chi tiết xuất kho
            ExportItem.objects.create(
                export_order=export_order,
                batch=batch,
                quantity=quantity,
                unit_price=unit_price
            )
            
            messages.success(request, 'Phiếu xuất kho đã được tạo thành công!')
            return redirect('inventory:export_list')
    
    # Lấy các lô hàng còn tồn kho
    batches = Batch.objects.filter(is_active=True, remaining_quantity__gt=0).order_by('expiry_date')
    context = {
        'batches': batches,
    }
    return render(request, 'inventory/export_form.html', context)

@login_required
def import_detail(request, pk):
    """Chi tiết phiếu nhập kho"""
    import_order = get_object_or_404(Import, pk=pk)
    import_items = import_order.items.all()
    
    # Tính toán ngày để so sánh
    today = timezone.now().date()
    expiring_soon = today + timezone.timedelta(days=30)
    
    context = {
        'import_order': import_order,
        'import_items': import_items,
        'today': today,
        'expiring_soon': expiring_soon,
    }
    return render(request, 'inventory/import_detail.html', context)

@login_required
def export_detail(request, pk):
    """Chi tiết phiếu xuất kho"""
    export_order = get_object_or_404(Export, pk=pk)
    export_items = export_order.items.all()
    
    context = {
        'export_order': export_order,
        'export_items': export_items,
    }
    return render(request, 'inventory/export_detail.html', context)

@login_required
def import_update(request, pk):
    """Chỉnh sửa phiếu nhập kho"""
    import_order = get_object_or_404(Import, pk=pk)
    
    if request.method == 'POST':
        # Xử lý cập nhật phiếu nhập
        import_order.supplier = request.POST.get('supplier', '')
        import_order.notes = request.POST.get('notes', '')
        import_order.save()
        
        # Xóa các ImportItem cũ
        import_order.items.all().delete()
        
        # Tạo chi tiết phiếu nhập mới
        product_id = request.POST.get('product')
        batch_code = request.POST.get('batch_code')
        quantity = request.POST.get('quantity')
        unit_price = request.POST.get('unit_price')
        expiry_date = request.POST.get('expiry_date')
        
        if product_id and batch_code and quantity and unit_price and expiry_date:
            product = Product.objects.get(id=product_id)
            quantity = int(quantity)
            unit_price = float(unit_price)
            
            # Cập nhật hoặc tạo lô hàng mới
            batch, created = Batch.objects.get_or_create(
                batch_code=batch_code,
                defaults={
                    'product': product,
                    'import_date': timezone.now().date(),
                    'expiry_date': expiry_date,
                    'import_price': unit_price,
                    'import_quantity': quantity,
                    'remaining_quantity': quantity,
                    'created_by': request.user
                }
            )
            
            if not created:
                # Cập nhật lô hàng hiện có
                batch.product = product
                batch.expiry_date = expiry_date
                batch.import_price = unit_price
                batch.import_quantity = quantity
                batch.remaining_quantity = quantity
                batch.save()
            
            # Tạo ImportItem mới
            ImportItem.objects.create(
                import_order=import_order,
                product=product,
                batch_code=batch_code,
                quantity=quantity,
                unit_price=unit_price,
                expiry_date=expiry_date
            )
        
        messages.success(request, f'Đã cập nhật phiếu nhập kho {import_order.import_code}')
        return redirect('inventory:import_list')
    
    products = Product.objects.filter(is_active=True)
    import_items = import_order.items.all()
    
    context = {
        'import_order': import_order,
        'import_items': import_items,
        'products': products,
    }
    return render(request, 'inventory/import_update.html', context)

@login_required
def import_delete(request, pk):
    """Xóa phiếu nhập kho"""
    import_order = get_object_or_404(Import, pk=pk)
    
    if request.method == 'POST':
        import_code = import_order.import_code
        print(f"Deleting import order: {import_code}")
        
        # Lấy danh sách batch codes trước khi xóa ImportItem
        batch_codes = list(import_order.items.values_list('batch_code', flat=True))
        print(f"Batch codes to delete: {batch_codes}")
        
        # Xóa các ImportItem trước
        items_deleted = import_order.items.all().delete()
        print(f"Deleted {items_deleted[0]} import items")
        
        # Xóa các Batch liên quan
        for batch_code in batch_codes:
            try:
                batch = Batch.objects.get(batch_code=batch_code)
                batch.delete()
                print(f"Deleted batch: {batch_code}")
            except Batch.DoesNotExist:
                print(f"Batch not found: {batch_code}")
                pass
        
        # Xóa phiếu nhập
        import_order.delete()
        print(f"Deleted import order: {import_code}")
        
        messages.success(request, f'Đã xóa phiếu nhập kho {import_code}')
        return redirect('inventory:import_list')
    
    context = {
        'import_order': import_order,
    }
    return render(request, 'inventory/import_confirm_delete.html', context)

@login_required
def export_update(request, pk):
    """Chỉnh sửa phiếu xuất kho"""
    export_order = get_object_or_404(Export, pk=pk)
    
    if request.method == 'POST':
        # Xử lý cập nhật phiếu xuất
        export_order.customer = request.POST.get('customer', '')
        export_order.notes = request.POST.get('notes', '')
        export_order.save()
        
        # Xóa các ExportItem cũ
        export_order.items.all().delete()
        
        # Tạo chi tiết phiếu xuất mới
        batch_id = request.POST.get('batch')
        quantity = request.POST.get('quantity')
        unit_price = request.POST.get('unit_price')
        
        if batch_id and quantity and unit_price:
            batch = Batch.objects.get(id=batch_id)
            quantity = int(quantity)
            unit_price = float(unit_price)
            
            # Kiểm tra số lượng tồn kho
            if batch.remaining_quantity >= quantity:
                # Cập nhật số lượng tồn kho
                batch.remaining_quantity -= quantity
                batch.save()
                
                # Tạo ExportItem mới
                ExportItem.objects.create(
                    export_order=export_order,
                    batch=batch,
                    quantity=quantity,
                    unit_price=unit_price
                )
            else:
                messages.error(request, f'Số lượng tồn kho không đủ. Tồn kho: {batch.remaining_quantity}')
                return redirect('inventory:export_update', pk=pk)
        
        messages.success(request, f'Đã cập nhật phiếu xuất kho {export_order.export_code}')
        return redirect('inventory:export_list')
    
    # Lấy danh sách batch có tồn kho
    batches = Batch.objects.filter(remaining_quantity__gt=0, is_active=True)
    export_items = export_order.items.all()
    
    context = {
        'export_order': export_order,
        'export_items': export_items,
        'batches': batches,
    }
    return render(request, 'inventory/export_update.html', context)

@login_required
def export_delete(request, pk):
    """Xóa phiếu xuất kho"""
    export_order = get_object_or_404(Export, pk=pk)
    
    if request.method == 'POST':
        export_code = export_order.export_code
        print(f"Deleting export order: {export_code}")
        
        # Hoàn trả số lượng tồn kho trước khi xóa
        for item in export_order.items.all():
            if item.batch:
                item.batch.remaining_quantity += item.quantity
                item.batch.save()
                print(f"Restored {item.quantity} to batch {item.batch.batch_code}")
        
        # Xóa các ExportItem
        items_deleted = export_order.items.all().delete()
        print(f"Deleted {items_deleted[0]} export items")
        
        # Xóa phiếu xuất
        export_order.delete()
        print(f"Deleted export order: {export_code}")
        
        messages.success(request, f'Đã xóa phiếu xuất kho {export_code}')
        return redirect('inventory:export_list')
    
    context = {
        'export_order': export_order,
    }
    return render(request, 'inventory/export_confirm_delete.html', context) 