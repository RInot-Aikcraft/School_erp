# widgets.py
from django_select2.forms import Select2MultipleWidget
from django.db.models import Value
from django.db.models.functions import Concat

class ParentSelectWidget(Select2MultipleWidget):
    """
    Widget personnalisé pour sélectionner plusieurs parents avec un parent principal
    """
    
    def __init__(self, *args, **kwargs):
        kwargs['data_view'] = 'parent-select2'  # Nous allons créer cette vue
        super().__init__(*args, **kwargs)
    
    def label_from_instance(self, obj):
        # Afficher le nom et prénom au lieu du username
        return f"{obj.first_name} {obj.last_name}"
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Ajouter l'attribut data-primary pour le parent principal
        if attrs:
            context['widget']['attrs']['data-primary'] = attrs.get('data-primary', '')
        return context