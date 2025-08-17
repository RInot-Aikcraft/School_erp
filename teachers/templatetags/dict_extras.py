from django import template

register = template.Library()

@register.filter
def getitem(dictionary, key):
    """
    Template filter to get a dictionary item by key.
    Usage: {{ dictionary|getitem:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None