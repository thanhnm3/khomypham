from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter để lấy giá trị từ dictionary bằng key có dấu cách"""
    return dictionary.get(key, '') 