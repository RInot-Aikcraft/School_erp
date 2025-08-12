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