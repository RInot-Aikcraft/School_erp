from django.db import models
from django.contrib.auth.models import User
from academics.models import ClassSubject
from django.core.validators import FileExtensionValidator

class ProgramChapter(models.Model):
    """
    Modèle pour représenter les chapitres du programme scolaire
    pour une matière spécifique dans une classe.
    """
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='program_chapters')
    title = models.CharField(max_length=200, verbose_name="Titre du chapitre")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Chapitre du programme"
        verbose_name_plural = "Chapitres du programme"
        ordering = ['order', 'title']
        unique_together = ('class_subject', 'title')
    
    def __str__(self):
        return f"{self.title} - {self.class_subject.subject.name} ({self.class_subject.class_obj.name})"

class Subtitle(models.Model):
    """
    Modèle pour représenter les sous-titres d'un chapitre
    """
    chapter = models.ForeignKey(ProgramChapter, on_delete=models.CASCADE, related_name='subtitles')
    title = models.CharField(max_length=300, verbose_name="Titre du sous-titre")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sous-titre"
        verbose_name_plural = "Sous-titres"
        ordering = ['order', 'title']
        unique_together = ('chapter', 'title')
    
    def __str__(self):
        return f"{self.title} - {self.chapter.title}"

class Interrogation(models.Model):
    """
    Modèle pour représenter une interrogation (examen)
    """
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='interrogations')
    chapter = models.ForeignKey(ProgramChapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='interrogations')
    title = models.CharField(max_length=200, verbose_name="Titre de l'interrogation")
    description = models.TextField(blank=True, verbose_name="Description")
    date = models.DateField(verbose_name="Date de l'interrogation")
    subject_pdf = models.FileField(
        upload_to='interrogation_subjects/%Y/%m/', 
        verbose_name="Sujet PDF",
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    total_points = models.PositiveIntegerField(default=20, verbose_name="Total des points")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Interrogation"
        verbose_name_plural = "Interrogations"
        ordering = ['-date', 'title']
    
    def __str__(self):
        return f"{self.title} - {self.class_subject.subject.name} ({self.date})"

class InterrogationGrade(models.Model):
    """
    Modèle pour représenter les notes des élèves à une interrogation
    """
    interrogation = models.ForeignKey(Interrogation, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interrogation_grades')
    points_earned = models.FloatField(verbose_name="Points obtenus")
    comments = models.TextField(blank=True, verbose_name="Commentaires")
    graded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Note d'interrogation"
        verbose_name_plural = "Notes d'interrogation"
        unique_together = ('interrogation', 'student')
    
    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} - {self.interrogation.title}: {self.points_earned}/{self.interrogation.total_points}"
    
    @property
    def percentage(self):
        """Calcule le pourcentage de la note"""
        if self.interrogation.total_points > 0:
            return (self.points_earned / self.interrogation.total_points) * 100
        return 0
    

class Textbook(models.Model):
    """Modèle pour le cahier de texte numérique"""
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='textbooks')
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='textbooks')
    date = models.DateField(auto_now_add=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cahier de texte"
        verbose_name_plural = "Cahiers de texte"
        ordering = ['-date']
    
    def __str__(self):
        return f"Cahier de texte - {self.class_subject.subject.name} - {self.class_subject.class_obj.name} - {self.date}"
    



class AttendanceStatus(models.TextChoices):
    PRESENT = 'PRESENT', 'Présent'
    ABSENT = 'ABSENT', 'Absent'
    LATE = 'LATE', 'En retard'

# teachers/models.py

class Attendance(models.Model):
    """
    Modèle pour suivre la présence des élèves lors des cours
    """
    textbook_entry = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(
        max_length=10, 
        choices=AttendanceStatus.choices
        # SUPPRIMEZ LA LIGNE : default=AttendanceStatus.PRESENT
    )
    comments = models.TextField(blank=True, verbose_name="Commentaires")
    
    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        unique_together = ('textbook_entry', 'student')
    
    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} - {self.get_status_display()} - {self.textbook_entry.date}"