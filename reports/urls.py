from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('inventory/export-excel/', views.export_inventory_excel, name='export_inventory_excel'),
    path('import-export/', views.import_export_report, name='import_export_report'),
    path('import-export/export-excel/', views.export_import_export_excel, name='export_import_export_excel'),
    path('profit/', views.profit_report, name='profit_report'),
    path('profit/export-excel/', views.export_profit_excel, name='export_profit_excel'),
] 