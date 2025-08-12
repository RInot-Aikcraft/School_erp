# Dans auth_app/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Filtre de template pour accéder à un élément d'un dictionnaire par sa clé.
    Exemple : {{ my_dict|lookup:my_key }}
    """
    # Vérifie si l'objet est un dictionnaire et si la clé existe
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None


@register.filter
def pprint(value):
    """Formatte une valeur pour le débogage."""
    import pprint
    return pprint.pformat(value)

@register.filter
def first(sequence):
    """Renvoie le premier élément d'une séquence."""
    try:
        return sequence[0]
    except (IndexError, TypeError):
        return None
    

@register.filter
def get_item(dictionary, key):
    """Retourne un élément d'un dictionnaire par sa clé."""
    return dictionary.get(key)