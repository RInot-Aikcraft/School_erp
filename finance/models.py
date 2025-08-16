from django.db import models
from academics.models import Class
from finance.templatetags.currency_filters import format_ariary
from school.models import SchoolYear
from django.contrib.auth.models import User

class TypeFrais(models.Model):
    id = models.AutoField(primary_key=True)
    nom_frais = models.CharField(max_length=100, verbose_name="Nom du frais")
    classe = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="Classe")
    annee_scolaire = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, verbose_name="Année scolaire")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant (Ar)")
    frais_inscription = models.BooleanField(default=False, verbose_name="Frais d'inscription")
    PERIODICITE_CHOICES = [
        ('MENSUEL', 'Mensuel'),
        ('TRIMESTRIEL', 'Trimestriel'),
        ('ANNUEL', 'Annuel'),
        ('PONCTUEL', 'Ponctuel'),
    ]
    periodicite = models.CharField(max_length=20, choices=PERIODICITE_CHOICES, verbose_name="Périodicité")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Type de frais"
        verbose_name_plural = "Types de frais"
        ordering = ['nom_frais']

    def __str__(self):
        return f"{self.nom_frais} - {self.classe.name} - {self.annee_scolaire.name}"


class TypeCaisse(models.Model):
    """Modèle pour représenter les différents types de caisses de l'école"""
    nom = models.CharField(max_length=100, verbose_name="Nom de la caisse")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    est_active = models.BooleanField(default=True, verbose_name="Active")
    couleur = models.CharField(max_length=7, default="#3498db", verbose_name="Couleur", 
                               help_text="Code hexadécimal de la couleur (ex: #3498db)")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Type de caisse"
        verbose_name_plural = "Types de caisses"
        ordering = ['nom']

    def __str__(self):
        return self.nom
    
class Paiement(models.Model):
    """Modèle pour enregistrer les paiements effectués par les élèves"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE', 'Validé'),
        ('ANNULE', 'Annulé'),
        ('REMBOURSE', 'Remboursé'),
    ]
    
    MODE_PAIEMENT_CHOICES = [
        ('ESPECE', 'Espèces'),
        ('CHEQUE', 'Chèque'),
        ('VIREMENT', 'Virement bancaire'),
        ('MOBILE', 'Paiement mobile'),
        ('AUTRE', 'Autre'),
    ]
    
    MOIS_CHOICES = [
        (1, 'Janvier'),
        (2, 'Février'),
        (3, 'Mars'),
        (4, 'Avril'),
        (5, 'Mai'),
        (6, 'Juin'),
        (7, 'Juillet'),
        (8, 'Août'),
        (9, 'Septembre'),
        (10, 'Octobre'),
        (11, 'Novembre'),
        (12, 'Décembre'),
    ]
    
    eleve = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paiements', verbose_name="Élève")
    type_frais = models.ForeignKey(TypeFrais, on_delete=models.CASCADE, related_name='paiements', verbose_name="Type de frais")
    type_caisse = models.ForeignKey(TypeCaisse, on_delete=models.CASCADE, related_name='paiements', verbose_name="Type de caisse")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant payé (Ar)")
    mois = models.PositiveSmallIntegerField(choices=MOIS_CHOICES, null=True, blank=True, verbose_name="Mois")
    date_paiement = models.DateTimeField(verbose_name="Date de paiement")
    date_enregistrement = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE', verbose_name="Statut")
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, verbose_name="Mode de paiement")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence (numéro de chèque, transaction, etc.)")
    notes = models.TextField(blank=True, verbose_name="Notes")
    enregistre_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='paiements_enregistres', verbose_name="Enregistré par")
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Paiement de {self.montant} par {self.eleve.get_full_name() or self.eleve.username} pour {self.type_frais.nom_frais}"
    
    def get_mois_display(self):
        """Retourne le nom du mois"""
        if self.mois:
            mois_dict = dict(self.MOIS_CHOICES)
            return mois_dict.get(self.mois, '')
        return ''
    

class Inscription(models.Model):
    """Modèle pour gérer les inscriptions des élèves"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('ACCEPTÉE', 'Acceptée'),
        ('REFUSÉE', 'Refusée'),
        ('CONFIRMÉE', 'Confirmée'),
        ('ANNULÉE', 'Annulée'),
    ]
    
    TYPE_INSCRIPTION_CHOICES = [
        ('PASSANT', 'Passant'),
        ('REDOUBLANT', 'Redoublant'),
    ]
    
    eleve = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscriptions', verbose_name="Élève")
    annee_scolaire = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='inscriptions', verbose_name="Année scolaire")
    classe_demandee = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='demandes_inscription', verbose_name="Classe demandée")
    classe_attribuee = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, related_name='inscriptions_attribuees', verbose_name="Classe attribuée")
    type_inscription = models.CharField(max_length=20, choices=TYPE_INSCRIPTION_CHOICES, default='PASSANT', verbose_name="Type d'inscription")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE', verbose_name="Statut")
    date_confirmation = models.DateTimeField(null=True, blank=True, verbose_name="Date de confirmation")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ['-date_inscription']
        # Un élève ne peut avoir qu'une seule inscription par année scolaire
        unique_together = ('eleve', 'annee_scolaire')
    
    def __str__(self):
        return f"Inscription de {self.eleve.get_full_name() or self.eleve.username} - {self.classe_demandee.name} ({self.annee_scolaire.name})"
    
    def get_statut_display(self):
        """Retourne le statut lisible"""
        statut_dict = dict(self.STATUT_CHOICES)
        return statut_dict.get(self.statut, '')
    
    def get_type_inscription_display(self):
        """Retourne le type d'inscription lisible"""
        type_dict = dict(self.TYPE_INSCRIPTION_CHOICES)
        return type_dict.get(self.type_inscription, '')
    
    # ... le reste de vos méthodes existantes ...
    
    def calculer_frais_inscription(self):
        """
        Calcule le montant total des frais d'inscription pour cette inscription
        en se basant uniquement sur les types de frais marqués comme frais d'inscription
        """
        types_frais = TypeFrais.objects.filter(
            classe=self.classe_demandee,
            annee_scolaire=self.annee_scolaire,
            frais_inscription=True  # Filtrer pour ne récupérer que les frais d'inscription
        )
        
        # Calculer le total
        total = sum(type_frais.montant for type_frais in types_frais)
        return total
    
    def get_types_frais(self):
        """
        Récupère uniquement les types de frais d'inscription associés à cette inscription
        """
        return TypeFrais.objects.filter(
            classe=self.classe_demandee,
            annee_scolaire=self.annee_scolaire,
            frais_inscription=True  # Filtrer pour ne récupérer que les frais d'inscription
        )
    
    def get_paiements(self):
        """
        Récupère tous les paiements associés aux frais d'inscription de cette inscription
        """
        types_frais_inscription = self.get_types_frais()
        return Paiement.objects.filter(
            eleve=self.eleve,
            type_frais__in=types_frais_inscription
        )
    
    def get_montant_paye(self):
        """
        Calcule le montant total payé pour les frais d'inscription de cette inscription
        """
        paiements = self.get_paiements()
        montant_paye = sum(paiement.montant for paiement in paiements if paiement.statut == 'VALIDE')
        return montant_paye
    
    def get_solde(self):
        """
        Calcule le solde restant à payer pour les frais d'inscription
        """
        return self.calculer_frais_inscription() - self.get_montant_paye()
    
    def est_complettement_paye(self):
        """
        Vérifie si les frais d'inscription sont complètement payés
        """
        return self.get_solde() <= 0
    
    def confirmer_inscription(self):
        """
        Confirme l'inscription et assigne l'élève à la classe demandée
        """
        from academics.models import Enrollment
        from django.utils import timezone
        
        # Vérifier si les frais d'inscription sont complètement payés
        if not self.est_complettement_paye():
            return False, "Les frais d'inscription ne sont pas complètement payés"
        
        # Vérifier s'il y a de la place dans la classe
        effectif_actuel = Enrollment.objects.filter(
            class_obj=self.classe_demandee,
            school_year=self.annee_scolaire,
            is_active=True
        ).count()
        
        if effectif_actuel >= self.classe_demandee.max_students:
            return False, "La classe est déjà complète"
        
        # Assigner la classe
        self.classe_attribuee = self.classe_demandee
        self.statut = 'CONFIRMÉE'
        self.date_confirmation = timezone.now()
        self.save()
        
        # Créer l'inscription académique
        Enrollment.objects.get_or_create(
            student=self.eleve,
            class_obj=self.classe_demandee,
            school_year=self.annee_scolaire,
            defaults={'is_active': True}
        )
        
        return True, "Inscription confirmée avec succès"
    

    def get_ecolages_impayes(self):
        """
        Récupère la liste de tous les mois de l'année scolaire avec leur statut de paiement
        en distinguant les mois à venir, en cours, ou passés
        """
        from datetime import date
        
        # Récupérer les types de frais d'écolage mensuels pour cette classe et cette année scolaire
        types_frais_ecolage = TypeFrais.objects.filter(
            classe=self.classe_demandee,
            annee_scolaire=self.annee_scolaire,
            periodicite='MENSUEL',  # On ne s'intéresse qu'aux frais mensuels
            frais_inscription=False
        )
        
        # Récupérer les paiements d'écolage mensuels déjà effectués
        paiements_ecolage = Paiement.objects.filter(
            eleve=self.eleve,
            type_frais__in=types_frais_ecolage,
            statut='VALIDE'
        )
        
        # Créer un dictionnaire des mois déjà payés avec leur montant
        mois_payes = {}
        for paiement in paiements_ecolage:
            if paiement.mois:
                mois_payes[paiement.mois] = paiement.montant
        
        # Récupérer la date actuelle
        aujourd_hui = date.today()
        
        # Liste pour stocker tous les mois avec leur statut
        tous_les_mois = []
        
        # Parcourir chaque mois de l'année scolaire
        current_date = self.annee_scolaire.start_date
        while current_date <= self.annee_scolaire.end_date:
            mois_courant = current_date.month
            annee_courante = current_date.year
            
            # Déterminer si le mois est à venir, en cours, ou passé
            statut_temporel = ""
            if current_date.year > aujourd_hui.year or (current_date.year == aujourd_hui.year and current_date.month > aujourd_hui.month):
                statut_temporel = "à_venir"
            elif current_date.year == aujourd_hui.year and current_date.month == aujourd_hui.month:
                statut_temporel = "en_cours"
            else:
                statut_temporel = "passé"
            
            # Déterminer le statut de paiement pour ce mois
            est_paye = mois_courant in mois_payes
            montant_paye = mois_payes.get(mois_courant, 0)
            
            # Calculer le montant dû pour ce mois (somme de tous les frais mensuels)
            montant_du = sum(type_frais.montant for type_frais in types_frais_ecolage)
            
            # Déterminer le statut affiché pour ce mois
            # MODIFICATION ICI : si le mois est payé, afficher "Payé" même si le mois est à venir
            if est_paye:
                statut_affiche = "Payé"
            elif statut_temporel == "à_venir":
                statut_affiche = "À venir"
            else:
                statut_affiche = "Impayé"
            
            # Ajouter le mois à la liste avec toutes les informations
            tous_les_mois.append({
                'mois': mois_courant,
                'annee': annee_courante,
                'nom_mois': dict(Paiement.MOIS_CHOICES).get(mois_courant, ''),
                'statut_temporel': statut_temporel,
                'est_paye': est_paye,
                'montant_du': montant_du,
                'montant_paye': montant_paye if est_paye else 0,
                'solde': montant_du - (montant_paye if est_paye else 0),
                'statut_affiche': statut_affiche
            })
            
            # Passer au mois suivant
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        return tous_les_mois