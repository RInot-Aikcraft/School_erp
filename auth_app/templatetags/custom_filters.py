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
def get_item(list_of_dicts, key):
    """
    Récupère un dictionnaire dans une liste en fonction de la valeur d'une clé.
    Exemple : list_of_dicts|get_item:1234 cherchera un dict où dict['id'] == 1234
    """
    if not isinstance(list_of_dicts, list):
        return None
    for item in list_of_dicts:
        # On suppose que la clé à chercher est 'time_slot_id' et que la valeur à comparer est un entier
        if item.get('time_slot_id') == int(key):
            return item
    return None
