from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Import
    path('import/', views.import_list, name='import_list'),
    path('import/create/', views.import_create, name='import_create'),
    path('import/<int:pk>/', views.import_detail, name='import_detail'),
    path('import/<int:pk>/update/', views.import_update, name='import_update'),
    path('import/<int:pk>/delete/', views.import_delete, name='import_delete'),
    
    # Export
    path('export/', views.export_list, name='export_list'),
    path('export/create/', views.export_create, name='export_create'),
    path('export/<int:pk>/', views.export_detail, name='export_detail'),
    path('export/<int:pk>/update/', views.export_update, name='export_update'),
    path('export/<int:pk>/delete/', views.export_delete, name='export_delete'),
] 