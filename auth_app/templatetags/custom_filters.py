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