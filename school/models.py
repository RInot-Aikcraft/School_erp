from django.db import models

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    principal_name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Établissement"
        verbose_name_plural = "Établissements"

class SchoolYear(models.Model):
    name = models.CharField(max_length=50)  # Ex: "2023-2024"
    start_date = models.DateField()
    end_date = models.DateField()
    current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"

class Period(models.Model):
    name = models.CharField(max_length=100)  # Ex: "Premier trimestre"
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='periods')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.school_year.name})"
    
    class Meta:
        verbose_name = "Période"
        verbose_name_plural = "Périodes"

class Holiday(models.Model):
    name = models.CharField(max_length=100)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='holidays')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.start_date} au {self.end_date})"
    
    class Meta:
        verbose_name = "Vacance"
        verbose_name_plural = "Vacances"