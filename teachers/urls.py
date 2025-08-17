from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('classes/', views.teacher_classes_list, name='classes_list'),
    path('classes/<int:pk>/', views.teacher_class_detail, name='class_detail'),
    path('schedule/', views.teacher_schedule, name='schedule'),
    # URLs pour le programme scolaire
    path('program/<int:class_subject_pk>/', views.teacher_program, name='program'),
    path('program/<int:class_subject_pk>/create/', views.teacher_create_chapter, name='create_chapter'),
    path('program/chapter/<int:chapter_pk>/edit/', views.teacher_edit_chapter, name='edit_chapter'),
    path('program/chapter/<int:chapter_pk>/delete/', views.teacher_delete_chapter, name='delete_chapter'),
    # URLs pour les sous-titres
    path('program/chapter/<int:chapter_pk>/subtitle/create/', views.teacher_create_subtitle, name='create_subtitle'),
    path('program/subtitle/<int:subtitle_pk>/edit/', views.teacher_edit_subtitle, name='edit_subtitle'),
    path('program/subtitle/<int:subtitle_pk>/delete/', views.teacher_delete_subtitle, name='delete_subtitle'),
    # URLs pour les interrogations
    path('interrogations/<int:class_subject_pk>/', views.teacher_interrogations, name='interrogations'),
    path('interrogations/create/<int:class_subject_pk>/', views.teacher_create_interrogation, name='create_interrogation'),
    path('interrogation/<int:pk>/', views.teacher_interrogation_detail, name='interrogation_detail'),
    path('interrogation/<int:pk>/edit/', views.teacher_edit_interrogation, name='edit_interrogation'),
    path('interrogation/<int:pk>/delete/', views.teacher_delete_interrogation, name='delete_interrogation'),
    path('interrogation/<int:interrogation_pk>/save-grades/', views.teacher_save_grades, name='save_grades'),
    # Corrigez l'URL pour la suppression de note
    path('interrogation/<int:interrogation_pk>/delete-grade/<int:student_id>/', views.teacher_delete_grade, name='delete_grade'),
    path('interrogation/<int:pk>/stats/', views.teacher_interrogation_stats, name='interrogation_stats'),

    # Ajoutez cette ligne à votre urlpatterns existant
    path('interrogation/<int:pk>/export-pdf/', views.teacher_interrogation_export_pdf, name='interrogation_export_pdf'),
    path('assignments/', views.teacher_assignments, name='assignments'),

    # URLs pour le cahier de texte
    path('textbook/create/', views.teacher_textbook_create, name='textbook_create'),
    path('textbook/<int:pk>/', views.teacher_textbook_detail, name='textbook_detail'),
    path('textbook/<int:pk>/edit/', views.teacher_textbook_edit, name='textbook_edit'),
    path('textbook/<int:pk>/delete/', views.teacher_textbook_delete, name='textbook_delete'),

    # URLs pour le cahier de texte par matière
    path('textbook/subject/<int:class_subject_pk>/', views.teacher_textbook_subject, name='textbook_subject'),
]
