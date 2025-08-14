from django import template

register = template.Library()

@register.filter
def format_ariary(value):
    """
    Formate un nombre en Ariary (MGA) avec des espaces comme séparateurs de milliers
    """
    try:
        # Convertir en float et formater avec 2 décimales
        formatted = "{:,.2f}".format(float(value))
        # Remplacer les virgules par des espaces pour les séparateurs de milliers
        formatted = formatted.replace(',', ' ')
        # Remplacer le point par une virgule pour les décimales
        formatted = formatted.replace('.', ',')
        return formatted + " Ar"
    except (ValueError, TypeError):
        return value