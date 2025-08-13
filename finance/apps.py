from django.apps import AppConfig
from django.db.models.signals import post_migrate

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'
    
    def ready(self):
        # Importer ici pour éviter les imports circulaires
        from .models import PaymentMethod
        
        # Connecter la fonction au signal post_migrate
        post_migrate.connect(create_default_payment_methods, sender=self)

def create_default_payment_methods(sender, **kwargs):
    """
    Crée des méthodes de paiement par défaut si elles n'existent pas.
    Cette fonction est appelée après que les migrations ont été appliquées.
    """
    from .models import PaymentMethod
    
    # Créer des méthodes de paiement par défaut si elles n'existent pas
    default_methods = ['Espèces', 'Chèque', 'Virement bancaire']
    for method_name in default_methods:
        PaymentMethod.objects.get_or_create(name=method_name)