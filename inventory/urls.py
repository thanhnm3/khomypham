from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Import
    path('import/', views.import_list, name='import_list'),
    path('import/create/', views.import_create, name='import_create'),
    path('import/manual/', views.import_manual_create, name='import_manual_create'),
    path('import/<int:pk>/add-items/', views.import_add_items, name='import_add_items'),
    path('import/<int:pk>/', views.import_detail, name='import_detail'),
    path('import/<int:pk>/update/', views.import_update, name='import_update'),
    path('import/<int:pk>/delete/', views.import_delete, name='import_delete'),
    path('import/excel/', views.import_excel, name='import_excel'),
    path('import/excel/confirm/', views.import_excel_confirm, name='import_excel_confirm'),
    
    # AJAX
    path('get-product-info/', views.get_product_info, name='get_product_info'),
    path('create-product-ajax/', views.create_product_ajax, name='create_product_ajax'),
    path('get-batch-info/<int:batch_id>/', views.get_batch_info, name='get_batch_info'),
    path('get-product-info/<int:product_id>/', views.get_product_info, name='get_product_info_detail'),
    
    # Export
    path('export/', views.export_list, name='export_list'),
    path('export/create/', views.export_create, name='export_create'),
    path('export/<int:pk>/add-items/', views.export_add_items, name='export_add_items'),
    path('export/<int:pk>/', views.export_detail, name='export_detail'),
    path('export/<int:pk>/update/', views.export_update, name='export_update'),
    path('export/<int:pk>/delete/', views.export_delete, name='export_delete'),
] 