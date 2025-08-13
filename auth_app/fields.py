from django import forms
from django_select2.forms import ModelSelect2MultipleField
from django.contrib.auth.models import User
from .widgets import ParentSelectWidget

class ParentSelectField(ModelSelect2MultipleField):
    """
    Champ personnalisé pour sélectionner plusieurs parents avec un parent principal
    """
    widget = ParentSelectWidget
    
    def __init__(self, *args, **kwargs):
        # Filtrer pour n'afficher que les utilisateurs de type parent
        queryset = User.objects.filter(userprofile__user_type='parent')
        super().__init__(queryset=queryset, *args, **kwargs)
    
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['data-primary'] = self.initial_primary if hasattr(self, 'initial_primary') else ''
        return attrs
    
    def value_from_datadict(self, data, files, name):
        # Récupérer les IDs des parents sélectionnés
        parent_ids = data.getlist(name + '[]', [])
        # Récupérer l'ID du parent principal
        primary_parent_id = data.get(name + '_primary', '')
        
        # Stocker l'ID du parent principal pour l'utiliser plus tard
        self.primary_parent_id = primary_parent_id
        
        return parent_ids
    
    def clean(self, value):
        # Nettoyer les valeurs
        value = super().clean(value)
        
        # S'assurer qu'au moins un parent est sélectionné
        if not value:
            raise forms.ValidationError("Veuillez sélectionner au moins un parent.")
        
        return value