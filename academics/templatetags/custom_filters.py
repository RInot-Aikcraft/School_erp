from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtre pour obtenir un élément d'un dictionnaire par sa clé.
    Usage: {{ my_dict|get_item:my_key }}
    """
    return dictionary.get(key)