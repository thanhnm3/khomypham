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