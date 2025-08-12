from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    # Définition des choix pour les champs à sélection multiple
    USER_TYPES = (
        ('admin', 'Administrateur'),
        ('teacher', 'Enseignant'),
        ('student', 'Élève'),
        ('parent', 'Parent'),
    )

    GENDER_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    )

    CIVIL_STATUS_CHOICES = (
        ('single', 'Célibataire'),
        ('married', 'Marié(e)'),
        ('divorced', 'Divorcé(e)'),
        ('widowed', 'Veuf(ve)'),
    )

    EMPLOYMENT_STATUS_CHOICES = (
        ('permanent', 'Permanent'),
        ('contract', 'Contractuel'),
        ('part_time', 'Temps partiel'),
        ('substitute', 'Remplaçant'),
    )

    # Champ de liaison avec le modèle User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    
    # Champs de base
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Informations personnelles supplémentaires
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    id_card_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro CIN / Passeport")
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES, blank=True, null=True)
    
    # Contact d'urgence
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Informations professionnelles (principalement pour les enseignants)
    internal_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Matricule interne")
    professional_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID professionnel")
    diplomas = models.TextField(blank=True, null=True, verbose_name="Diplômes et formations")
    hire_date = models.DateField(blank=True, null=True, verbose_name="Date d'embauche")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Poste occupé")
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, blank=True, null=True, verbose_name="Statut d'emploi")
    experience_years = models.IntegerField(blank=True, null=True, verbose_name="Années d'expérience")
    previous_positions = models.TextField(blank=True, null=True, verbose_name="Expériences professionnelles précédentes")

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

# Signaux pour créer automatiquement un profil utilisateur lorsqu'un utilisateur est créé
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Vérifiez si le profil existe avant de tenter de le sauvegarder
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        # Si le profil n'existe pas, créez-le
        UserProfile.objects.create(user=instance)
