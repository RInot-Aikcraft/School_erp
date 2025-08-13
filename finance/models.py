from django.db import models
from django.conf import settings
from academics.models import Class  # Correction: import depuis academics.models

class FeeType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du frais")
    description = models.TextField(blank=True, verbose_name="Description")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Type de frais"
        verbose_name_plural = "Types de frais"

class FeeStructure(models.Model):
    classroom = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="Classe")  # Correction: utiliser Class au lieu de Classroom
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, verbose_name="Type de frais")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    academic_year = models.CharField(max_length=20, verbose_name="Année académique")
    
    def __str__(self):
        return f"{self.classroom.name} - {self.fee_type.name} - {self.academic_year}"
    
    class Meta:
        verbose_name = "Structure de frais"
        verbose_name_plural = "Structures de frais"
        unique_together = ('classroom', 'fee_type', 'academic_year')

class Fee(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, verbose_name="Élève")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, verbose_name="Structure de frais")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant dû")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant payé")
    balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Solde")
    status = models.CharField(max_length=20, choices=[('unpaid', 'Non payé'), ('partially_paid', 'Partiellement payé'), ('paid', 'Payé')], default='unpaid', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    def save(self, *args, **kwargs):
        self.balance = self.amount_due - self.amount_paid
        if self.balance <= 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
        else:
            self.status = 'unpaid'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.fee_structure.fee_type.name} - {self.fee_structure.academic_year}"
    
    class Meta:
        verbose_name = "Frais"
        verbose_name_plural = "Frais"

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, verbose_name="Méthode de paiement")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Méthode de paiement"
        verbose_name_plural = "Méthodes de paiement"

class Payment(models.Model):
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, verbose_name="Frais")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name="Méthode de paiement")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Date de paiement")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    def __str__(self):
        return f"Paiement de {self.amount} pour {self.fee.student.get_full_name()}"
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"