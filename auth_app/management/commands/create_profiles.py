from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from auth_app.models import UserProfile

class Command(BaseCommand):
    help = 'Crée des profils utilisateur pour tous les utilisateurs qui n\'en ont pas'

    def handle(self, *args, **options):
        for user in User.objects.all():
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Profil créé pour l\'utilisateur: {user.username}'))
            else:
                self.stdout.write(self.style.NOTICE(f'L\'utilisateur {user.username} a déjà un profil'))