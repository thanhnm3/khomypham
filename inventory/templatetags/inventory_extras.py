from django import template
from django.forms import BoundField

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter để lấy giá trị từ dictionary bằng key có dấu cách"""
    return dictionary.get(key, '')

@register.filter
def get_field_value(form, index):
    """Template filter để hiển thị field category với styling phù hợp"""
    field_name = f'category_{index}'
    if field_name in form.fields:
        field = form[field_name]
        # Thêm class CSS dựa trên loại field
        if hasattr(field.field, 'queryset'):
            # ModelChoiceField - danh mục tồn tại
            field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' category-exists'
        else:
            # ChoiceField - danh mục không tồn tại
            field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' category-missing'
        return field
    return ''

@register.filter
def get_unit_field_value(form, index):
    """Template filter để hiển thị field unit với styling phù hợp"""
    field_name = f'unit_{index}'
    if field_name in form.fields:
        field = form[field_name]
        # Thêm class CSS dựa trên validation
        if field.errors:
            field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' is-invalid'
        return field
    return ''

@register.filter
def get_expiry_field_value(form, index):
    """Template filter để hiển thị field expiry_date với styling phù hợp"""
    field_name = f'expiry_date_{index}'
    if field_name in form.fields:
        field = form[field_name]
        # Thêm class CSS dựa trên validation
        if field.errors:
            field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' is-invalid'
        return field
    return ''

@register.filter
def get_product_name_field_value(form, index):
    """Template filter để hiển thị field product_name với styling phù hợp"""
    field_name = f'product_name_{index}'
    if field_name in form.fields:
        field = form[field_name]
        # Thêm class CSS dựa trên validation
        if field.errors:
            field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' is-invalid'
        return field
    return ''

@register.filter
def get_quantity_field_value(form, index):
    """Template filter để hiển thị field quantity với styling phù hợp"""
    field_name = f'quantity_{index}'
    if field_name in form.fields:
        field = form[field_name]
        # Thêm class CSS dựa trên validation
        if field.errors:
            field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' is-invalid'
        return field
    return ''

@register.filter
def get_import_price_field_value(form, index):
    """Template filter để hiển thị field import_price với styling phù hợp"""
    field_name = f'import_price_{index}'
    if field_name in form.fields:
        field = form[field_name]
        # Thêm class CSS dựa trên validation
        if field.errors:
            field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' is-invalid'
        return field
    return ''

@register.filter
def get_selling_price_field_value(form, index):
    """Template filter để hiển thị field selling_price với styling phù hợp"""
    field_name = f'selling_price_{index}'
    if field_name in form.fields:
        field = form[field_name]
        # Thêm class CSS dựa trên validation
        if field.errors:
            field.field.widget.attrs['class'] = field.field.widget.attrs.get('class', '') + ' is-invalid'
        return field
    return '' 