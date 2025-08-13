from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from school.models import SchoolYear, Period


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"


# Dans academics/models.py
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#3498db", help_text="Code hexadécimal de la couleur (ex: #3498db)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"

class ClassLevel(models.Model):
    name = models.CharField(max_length=50)  # Ex: "6ème", "5ème", etc.
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"

class Class(models.Model):
    name = models.CharField(max_length=50)  # Ex: "6ème A", "5ème B", etc.
    level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='classes')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='classes')
    main_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='main_classes')
    max_students = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.school_year.name})"
    
    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.class_obj.name}"
    
    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ('student', 'class_obj', 'school_year')

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assignments')
    due_date = models.DateTimeField()
    total_points = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    class Meta:
        verbose_name = "Devoir"
        verbose_name_plural = "Devoirs"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='grades')
    points_earned = models.FloatField()
    comments = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}: {self.points_earned}/{self.assignment.total_points}"
    
    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        unique_together = ('student', 'assignment')

class TeacherSubject(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teachers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Matière enseignée"
        verbose_name_plural = "Matières enseignées"
        unique_together = ('teacher', 'subject')
    
    def __str__(self):
        # CORRECTION : Ajout des parenthèses pour appeler la méthode get_full_name()
        return f"{self.teacher.get_full_name() or self.teacher.username} - {self.subject.name}"

# MODÈLE AJOUTÉ : TeacherSubjectLevel
class TeacherSubjectLevel(models.Model):
    """
    Modèle intermédiaire pour associer un enseignant-matière à un niveau d'enseignement.
    Permet de savoir qu'un enseignant enseigne une matière spécifique à des niveaux spécifiques.
    """
    teacher_subject = models.ForeignKey(TeacherSubject, on_delete=models.CASCADE, related_name='levels')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='teacher_subject_levels')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Niveau d'enseignement"
        verbose_name_plural = "Niveaux d'enseignement"
        # Un enseignant ne peut pas enseigner la même matière au même niveau deux fois
        unique_together = ('teacher_subject', 'class_level')
        
    def __str__(self):
        return f"{self.teacher_subject.teacher.get_full_name() or self.teacher_subject.teacher.username} - {self.teacher_subject.subject.name} ({self.class_level.name})"
    

class ClassSubject(models.Model):
    """
    Modèle pour associer une matière et un enseignant à une classe spécifique
    pour une année scolaire donnée.
    Ex: M. Dupont (enseignant) enseigne les Mathématiques (matière) à la classe 6ème A (classe)
    pendant l'année scolaire 2023-2024.
    """
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_assignments')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='class_subjects')
    
    # --- AJOUT DU COEFFICIENT ---
    coefficient = models.PositiveIntegerField(
        default=1,
        help_text="Coefficient de la matière pour le calcul de la moyenne."
    )

    class Meta:
        verbose_name = "Matière de classe"
        verbose_name_plural = "Matières de classe"
        unique_together = ('class_obj', 'subject', 'school_year')

    def __str__(self):
        return f"{self.subject.name} - {self.class_obj.name} ({self.teacher.get_full_name() or self.teacher.username}) [Coeff: {self.coefficient}]"
    

class TimeSlot(models.Model):
    """
    Définit un créneau horaire pour la journée.
    Ex: 08:00 - 09:00, 09:00 - 10:00, etc.
    """
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        verbose_name = "Créneau Horaire"
        verbose_name_plural = "Créneaux Horaires"
        ordering = ['start_time']
        
    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class Schedule(models.Model):
    """
    Représente l'emploi du temps d'une classe pour une année scolaire donnée.
    Une classe n'a qu'un seul emploi du temps par année scolaire.
    """
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='schedules')
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='schedules')
    
    class Meta:
        verbose_name = "Emploi du Temps"
        verbose_name_plural = "Emplois du Temps"
        unique_together = ('class_obj', 'school_year') # Une classe n'a qu'un emploi du temps par an
        
    def __str__(self):
        return f"Emploi du temps - {self.class_obj.name} ({self.school_year.name})"

class ScheduleEntry(models.Model):
    """
    Une entrée spécifique dans l'emploi du temps.
    Associe un créneau horaire, un jour de la semaine et une matière (ClassSubject) à un emploi du temps.
    """
    DAYS_OF_WEEK = [
        ('1', 'Lundi'),
        ('2', 'Mardi'),
        ('3', 'Mercredi'),
        ('4', 'Jeudi'),
        ('5', 'Vendredi'),
        ('6', 'Samedi'),
        ('7', 'Dimanche'),
    ]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='entries')
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='schedule_entries')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='schedule_entries')
    day_of_week = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
    
    class Meta:
        verbose_name = "Entrée d'Emploi du Temps"
        verbose_name_plural = "Entrées d'Emploi du Temps"
        # Empêcher d'avoir deux cours au même moment dans la même classe
        unique_together = ('schedule', 'day_of_week', 'time_slot')
        ordering = ['day_of_week', 'time_slot__start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.time_slot} - {self.class_subject.subject.name}"