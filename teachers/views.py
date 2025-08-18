from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse 
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import Prefetch

from academics.models import (
    ClassSubject, ScheduleEntry, Enrollment, Class,
    Schedule, TimeSlot, Assignment, Grade
)
from school.models import SchoolYear
from finance.models import Inscription
from .models import (
    ProgramChapter, Subtitle, Interrogation, InterrogationGrade,
    Textbook, AttendanceStatus, Attendance
)

from django.core.paginator import Paginator
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os


@login_required
def teacher_dashboard(request):
    """
    Vue pour le tableau de bord du professeur
    """
    teacher = request.user
    today = timezone.now().date()
    
    # Récupérer l'année scolaire active
    active_school_year = SchoolYear.objects.filter(current=True).first()
    if not active_school_year:
        active_school_year = SchoolYear.objects.first()
    
    # Compter les classes du professeur
    teacher_classes_count = ClassSubject.objects.filter(
        teacher=teacher,
        school_year=active_school_year
    ).values('class_obj').distinct().count()
    
    # Compter les matières du professeur
    teacher_subjects_count = ClassSubject.objects.filter(
        teacher=teacher,
        school_year=active_school_year
    ).count()
    
    # Compter le nombre total d'élèves dans les classes du professeur
    total_students = Inscription.objects.filter(
        classe_demandee__class_subjects__teacher=teacher,
        annee_scolaire=active_school_year
    ).distinct().count()
    
    # Calculer la moyenne d'élèves par classe
    average_students_per_class = total_students / teacher_classes_count if teacher_classes_count > 0 else 0
    
    # Compter le nombre total de cours du professeur
    total_courses = ScheduleEntry.objects.filter(
        class_subject__teacher=teacher,
        schedule__school_year=active_school_year
    ).count()
    
    # Compter le nombre de cours cette semaine
    start_of_week = today - timezone.timedelta(days=today.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=6)
    courses_this_week = ScheduleEntry.objects.filter(
        class_subject__teacher=teacher,
        schedule__school_year=active_school_year,
        day_of_week__in=[str(i) for i in range(1, 8)]
    ).count()
    
    # Récupérer les prochains cours (pour les 7 prochains jours)
    upcoming_classes = ScheduleEntry.objects.filter(
        class_subject__teacher=teacher,
        schedule__school_year=active_school_year,
        day_of_week__in=[str((today.weekday() + i) % 7 + 1) for i in range(7)]
    ).select_related(
        'class_subject__subject',
        'class_subject__class_obj',
        'time_slot'
    ).order_by('day_of_week', 'time_slot__start_time')
    
    # Ajouter le nom du jour de la semaine pour l'affichage
    days_of_week = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    for class_item in upcoming_classes:
        class_item.day_of_week_display = days_of_week[int(class_item.day_of_week) - 1]
    
    # Récupérer les interrogations à venir (pour les 30 prochains jours)
    upcoming_interrogations = Interrogation.objects.filter(
        class_subject__teacher=teacher,
        date__gt=today,
        date__lte=today + timezone.timedelta(days=30)
    ).select_related(
        'class_subject__subject',
        'class_subject__class_obj',
        'chapter'
    ).order_by('date')
    
    # Récupérer l'emploi du temps du jour
    today_day_of_week = str(today.weekday() + 1)  # Django utilise 1-7 pour lundi-dimanche
    today_schedule = ScheduleEntry.objects.filter(
        class_subject__teacher=teacher,
        schedule__school_year=active_school_year,
        day_of_week=today_day_of_week
    ).select_related(
        'class_subject__subject',
        'class_subject__class_obj',
        'time_slot'
    ).order_by('time_slot__start_time')
    
    # Récupérer les dernières notes enregistrées
    recent_grades = Grade.objects.filter(
        assignment__teacher=teacher
    ).select_related(
        'student',
        'assignment'
    ).order_by('-graded_at')[:10]
    
    # Calculer les pourcentages pour chaque note
    for grade in recent_grades:
        grade.percentage = (grade.points_earned / grade.assignment.total_points) * 100 if grade.assignment.total_points > 0 else 0
    
    context = {
        'today': today,
        'teacher_classes_count': teacher_classes_count,
        'teacher_subjects_count': teacher_subjects_count,
        'total_students': total_students,
        'average_students_per_class': average_students_per_class,
        'total_courses': total_courses,
        'courses_this_week': courses_this_week,
        'upcoming_classes': upcoming_classes,
        'upcoming_interrogations': upcoming_interrogations,
        'today_schedule': today_schedule,
        'recent_grades': recent_grades,
        'active_school_year': active_school_year,
    }
    
    return render(request, 'teachers/dashboard.html', context)


@login_required
def teacher_classes_list(request):
    """
    Vue pour lister toutes les classes du professeur
    """
    teacher = request.user
    
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active ou la plus récente
    active_school_year = SchoolYear.objects.filter(current=True).first()
    if not active_school_year and school_years:
        active_school_year = school_years.first()
    
    # Récupérer l'année scolaire sélectionnée (depuis les paramètres GET ou l'année active par défaut)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        selected_year = get_object_or_404(SchoolYear, pk=selected_year_id)
    else:
        selected_year = active_school_year
    
    # Récupérer les matières enseignées par ce professeur pour l'année scolaire sélectionnée
    teacher_subjects = ClassSubject.objects.filter(
        teacher=teacher,
        school_year=selected_year
    ).select_related('class_obj', 'subject', 'school_year')
    
    # Organiser les données par classe
    classes_data = {}
    for subject in teacher_subjects:
        class_obj = subject.class_obj
        if class_obj.id not in classes_data:
            classes_data[class_obj.id] = {
                'class_obj': class_obj,
                'subjects': []
            }
        classes_data[class_obj.id]['subjects'].append(subject)
    
    context = {
        'classes_data': classes_data,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
    }
    
    return render(request, 'teachers/classes/list.html', context)

@login_required
def teacher_class_detail(request, pk):
    """
    Vue pour afficher les détails d'une classe spécifique pour un professeur
    """
    teacher = request.user
    class_obj = get_object_or_404(Class, pk=pk)
    
    # Vérifier que le professeur enseigne bien dans cette classe
    if not ClassSubject.objects.filter(teacher=teacher, class_obj=class_obj).exists():
        messages.error(request, "Vous n'êtes pas autorisé à voir cette classe.")
        return redirect('teachers:classes_list')
    
    # Récupérer l'année scolaire active
    active_school_year = SchoolYear.objects.filter(current=True).first()
    if not active_school_year:
        active_school_year = SchoolYear.objects.first()
    
    # Récupérer les matières enseignées par ce professeur dans cette classe
    teacher_subjects = ClassSubject.objects.filter(
        teacher=teacher,
        class_obj=class_obj,
        school_year=active_school_year
    ).select_related('subject')
    
    # Récupérer les inscriptions des élèves dans cette classe pour l'année scolaire active
    inscriptions = Inscription.objects.filter(
        classe_demandee=class_obj,
        annee_scolaire=active_school_year
    ).select_related('eleve__userprofile')
    
    enrolled_students_count = inscriptions.count()
    
    if class_obj.max_students > 0:
        occupancy_percentage = (enrolled_students_count / class_obj.max_students) * 100
    else:
        occupancy_percentage = 0
    
    # Récupérer les entrées du cahier de texte pour chaque matière
    for subject in teacher_subjects:
        subject.textbook_entries = Textbook.objects.filter(
            teacher=teacher,
            class_subject=subject
        ).order_by('-date')
    
    # Récupérer les devoirs récents pour cette classe dans les matières du professeur
    recent_assignments = Assignment.objects.filter(
        class_obj=class_obj,
        subject__in=teacher_subjects.values_list('subject', flat=True)
    ).order_by('-due_date')[:5]
    
    # Récupérer les notes récentes données par ce professeur dans cette classe
    recent_grades = Grade.objects.filter(
        assignment__class_obj=class_obj,
        assignment__teacher=teacher
    ).select_related('student', 'assignment').order_by('-graded_at')[:10]
    
    # Calculer les pourcentages pour chaque note
    for grade in recent_grades:
        grade.percentage = (grade.points_earned / grade.assignment.total_points) * 100 if grade.assignment.total_points > 0 else 0
    
    context = {
        'class_obj': class_obj,
        'teacher_subjects': teacher_subjects,
        'inscriptions': inscriptions,
        'enrolled_students_count': enrolled_students_count,
        'occupancy_percentage': occupancy_percentage,
        'recent_assignments': recent_assignments,
        'recent_grades': recent_grades,
        'active_school_year': active_school_year,
    }
    
    return render(request, 'teachers/classes/detail.html', context)

@login_required
def teacher_schedule(request):
    """
    Vue pour afficher l'emploi du temps du professeur
    """
    teacher = request.user
    
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active ou la plus récente
    active_school_year = SchoolYear.objects.filter(current=True).first()
    if not active_school_year and school_years:
        active_school_year = school_years.first()
    
    # Récupérer l'année scolaire sélectionnée (depuis les paramètres GET ou l'année active par défaut)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        selected_year = get_object_or_404(SchoolYear, pk=selected_year_id)
    else:
        selected_year = active_school_year
    
    # Récupérer tous les cours du professeur pour l'année scolaire sélectionnée
    schedule_entries = ScheduleEntry.objects.filter(
        class_subject__teacher=teacher,
        schedule__school_year=selected_year
    ).select_related(
        'class_subject__subject',
        'class_subject__class_obj',
        'time_slot'
    ).order_by('day_of_week', 'time_slot__start_time')
    
    # Récupérer tous les créneaux horaires disponibles
    time_slots = TimeSlot.objects.all().order_by('start_time')
    
    # Organiser les entrées par jour
    schedule_by_day = {}
    days_of_week = [
        ('1', 'Lundi'), ('2', 'Mardi'), ('3', 'Mercredi'),
        ('4', 'Jeudi'), ('5', 'Vendredi'), ('6', 'Samedi'), ('7', 'Dimanche'),
    ]
    
    # Initialiser la structure
    for day_num, day_name in days_of_week:
        schedule_by_day[day_num] = {
            'name': day_name,
            'entries': []
        }
    
    # Remplir avec les entrées existantes
    for entry in schedule_entries:
        day_num = entry.day_of_week
        if day_num in schedule_by_day:
            schedule_by_day[day_num]['entries'].append(entry)
    
    context = {
        'schedule_by_day': schedule_by_day,
        'days_of_week': days_of_week,
        'time_slots': time_slots,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
    }
    
    return render(request, 'teachers/schedule/list.html', context)

@login_required
def teacher_assignments(request):
    """
    Vue pour lister tous les devoirs du professeur
    """
    teacher = request.user
    
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active ou la plus récente
    active_school_year = SchoolYear.objects.filter(current=True).first()
    if not active_school_year and school_years:
        active_school_year = school_years.first()
    
    # Récupérer l'année scolaire sélectionnée (depuis les paramètres GET ou l'année active par défaut)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        selected_year = get_object_or_404(SchoolYear, pk=selected_year_id)
    else:
        selected_year = active_school_year
    
    # Récupérer tous les devoirs du professeur pour l'année scolaire sélectionnée
    assignments = Assignment.objects.filter(
        teacher=teacher,
        class_obj__school_year=selected_year
    ).select_related(
        'subject',
        'class_obj'
    ).order_by('-due_date')
    
    context = {
        'assignments': assignments,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
    }
    
    return render(request, 'teachers/assignments/list.html', context)

@login_required
def teacher_class_detail(request, pk):
    """
    Vue pour afficher les détails d'une classe spécifique pour un professeur
    """
    teacher = request.user
    class_obj = get_object_or_404(Class, pk=pk)
    
    # Vérifier que le professeur enseigne bien dans cette classe
    if not ClassSubject.objects.filter(teacher=teacher, class_obj=class_obj).exists():
        messages.error(request, "Vous n'êtes pas autorisé à voir cette classe.")
        return redirect('teachers:classes_list')
    
    # Récupérer l'année scolaire active
    active_school_year = SchoolYear.objects.filter(current=True).first()
    if not active_school_year:
        active_school_year = SchoolYear.objects.first()
    
    # Récupérer les matières enseignées par ce professeur dans cette classe
    teacher_subjects = ClassSubject.objects.filter(
        teacher=teacher,
        class_obj=class_obj,
        school_year=active_school_year
    ).select_related('subject')
    
    # Récupérer les inscriptions des élèves dans cette classe pour l'année scolaire active
    inscriptions = Inscription.objects.filter(
        classe_demandee=class_obj,
        annee_scolaire=active_school_year
    ).select_related('eleve__userprofile')
    
    enrolled_students_count = inscriptions.count()
    
    if class_obj.max_students > 0:
        occupancy_percentage = (enrolled_students_count / class_obj.max_students) * 100
    else:
        occupancy_percentage = 0
    
    # Récupérer les entrées du cahier de texte pour chaque matière, triées par date décroissante
    for subject in teacher_subjects:
        subject.textbook_entries = Textbook.objects.filter(
            teacher=teacher,
            class_subject=subject
        ).order_by('-date')  # Tri par date décroissante
    
    # Récupérer les devoirs récents pour cette classe dans les matières du professeur
    recent_assignments = Assignment.objects.filter(
        class_obj=class_obj,
        subject__in=teacher_subjects.values_list('subject', flat=True)
    ).order_by('-due_date')[:5]
    
    # Récupérer les notes récentes données par ce professeur dans cette classe
    recent_grades = Grade.objects.filter(
        assignment__class_obj=class_obj,
        assignment__teacher=teacher
    ).select_related('student', 'assignment').order_by('-graded_at')[:10]
    
    # Calculer les pourcentages pour chaque note
    for grade in recent_grades:
        grade.percentage = (grade.points_earned / grade.assignment.total_points) * 100 if grade.assignment.total_points > 0 else 0
    
    context = {
        'class_obj': class_obj,
        'teacher_subjects': teacher_subjects,
        'inscriptions': inscriptions,
        'enrolled_students_count': enrolled_students_count,
        'occupancy_percentage': occupancy_percentage,
        'recent_assignments': recent_assignments,
        'recent_grades': recent_grades,
        'active_school_year': active_school_year,
    }
    
    return render(request, 'teachers/classes/detail.html', context)

@login_required
def teacher_assignment_create(request):
    """
    Vue pour créer un nouveau devoir
    """
    teacher = request.user
    
    # Récupérer les classes où le professeur enseigne
    teacher_classes = ClassSubject.objects.filter(
        teacher=teacher
    ).select_related('class_obj', 'subject')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        class_subject_id = request.POST.get('class_subject')
        due_date = request.POST.get('due_date')
        total_points = request.POST.get('total_points', 100)
        
        class_subject = get_object_or_404(ClassSubject, pk=class_subject_id)
        
        # Vérifier que le professeur enseigne bien dans cette classe
        if class_subject.teacher != teacher:
            messages.error(request, "Vous n'êtes pas autorisé à créer un devoir pour cette classe.")
            return redirect('teachers:assignment_create')
        
        Assignment.objects.create(
            title=title,
            description=description,
            subject=class_subject.subject,
            teacher=teacher,
            class_obj=class_subject.class_obj,
            due_date=due_date,
            total_points=total_points
        )
        
        messages.success(request, 'Devoir créé avec succès!')
        return redirect('teachers:assignments')
    
    context = {
        'teacher_classes': teacher_classes,
    }
    
    return render(request, 'teachers/assignments/form.html', context)

@login_required
def teacher_grade_create(request, assignment_pk):
    """
    Vue pour créer ou modifier des notes pour un devoir
    """
    teacher = request.user
    assignment = get_object_or_404(Assignment, pk=assignment_pk)
    
    # Vérifier que le professeur est bien l'auteur du devoir
    if assignment.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à noter ce devoir.")
        return redirect('teachers:assignments')
    
    # Récupérer les élèves inscrits dans la classe
    inscriptions = Inscription.objects.filter(
        classe_demandee=assignment.class_obj,
        annee_scolaire=assignment.class_obj.school_year
    ).select_related('eleve')
    
    if request.method == 'POST':
        # Traiter les notes soumises
        for inscription in inscriptions:
            student_id = inscription.eleve.id
            points_earned = request.POST.get(f'points_{student_id}')
            comments = request.POST.get(f'comments_{student_id}', '')
            
            if points_earned is not None and points_earned != '':
                # Mettre à jour ou créer la note
                Grade.objects.update_or_create(
                    student=inscription.eleve,
                    assignment=assignment,
                    defaults={
                        'points_earned': float(points_earned),
                        'comments': comments
                    }
                )
        
        messages.success(request, 'Notes enregistrées avec succès!')
        return redirect('teachers:assignment_detail', pk=assignment.pk)
    
    # Récupérer les notes existantes pour les afficher dans le formulaire
    existing_grades = {}
    for grade in assignment.grades.all():
        existing_grades[grade.student.id] = {
            'points_earned': grade.points_earned,
            'comments': grade.comments
        }
    
    context = {
        'assignment': assignment,
        'inscriptions': inscriptions,
        'existing_grades': existing_grades,
    }
    
    return render(request, 'teachers/grades/form.html', context)



@login_required
def teacher_program(request, class_subject_pk):
    """
    Vue pour afficher et gérer le programme scolaire pour une matière spécifique dans une classe
    """
    teacher = request.user
    class_subject = get_object_or_404(ClassSubject, pk=class_subject_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à ce programme.")
        return redirect('teachers:class_detail', pk=class_subject.class_obj.pk)
    
    # Récupérer tous les chapitres du programme pour cette matière et cette classe
    chapters = ProgramChapter.objects.filter(
        class_subject=class_subject
    ).prefetch_related('subtitles').order_by('order')
    
    context = {
        'class_subject': class_subject,
        'chapters': chapters,
    }
    
    return render(request, 'teachers/program/list.html', context)

@login_required
def teacher_create_chapter(request, class_subject_pk):
    """
    Vue pour créer un nouveau chapitre dans le programme scolaire
    """
    teacher = request.user
    class_subject = get_object_or_404(ClassSubject, pk=class_subject_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à ajouter des chapitres à ce programme.")
        return redirect('teachers:class_detail', pk=class_subject.class_obj.pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        order = request.POST.get('order', 1)
        
        # Calculer l'ordre si non spécifié
        if not order:
            last_chapter = ProgramChapter.objects.filter(
                class_subject=class_subject
            ).order_by('-order').first()
            order = (last_chapter.order + 1) if last_chapter else 1
        
        chapter = ProgramChapter.objects.create(
            class_subject=class_subject,
            title=title,
            order=order
        )
        
        messages.success(request, 'Chapitre ajouté avec succès!')
        return redirect('teachers:program', class_subject_pk=class_subject.pk)
    
    # Récupérer le dernier ordre pour suggérer le prochain
    last_chapter = ProgramChapter.objects.filter(
        class_subject=class_subject
    ).order_by('-order').first()
    suggested_order = (last_chapter.order + 1) if last_chapter else 1
    
    context = {
        'class_subject': class_subject,
        'suggested_order': suggested_order,
    }
    
    return render(request, 'teachers/program/create_chapter.html', context)

@login_required
def teacher_edit_chapter(request, chapter_pk):
    """
    Vue pour modifier un chapitre du programme scolaire
    """
    teacher = request.user
    chapter = get_object_or_404(ProgramChapter, pk=chapter_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if chapter.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce chapitre.")
        return redirect('teachers:program', class_subject_pk=chapter.class_subject.pk)
    
    if request.method == 'POST':
        chapter.title = request.POST.get('title', chapter.title)
        chapter.order = request.POST.get('order', chapter.order)
        
        chapter.save()
        messages.success(request, 'Chapitre mis à jour avec succès!')
        return redirect('teachers:program', class_subject_pk=chapter.class_subject.pk)
    
    context = {
        'chapter': chapter,
        'class_subject': chapter.class_subject,
    }
    
    return render(request, 'teachers/program/edit_chapter.html', context)

@login_required
def teacher_delete_chapter(request, chapter_pk):
    """
    Vue pour supprimer un chapitre du programme scolaire
    """
    teacher = request.user
    chapter = get_object_or_404(ProgramChapter, pk=chapter_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if chapter.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce chapitre.")
        return redirect('teachers:program', class_subject_pk=chapter.class_subject.pk)
    
    if request.method == 'POST':
        class_subject_pk = chapter.class_subject.pk
        chapter.delete()
        messages.success(request, 'Chapitre supprimé avec succès!')
        return redirect('teachers:program', class_subject_pk=class_subject_pk)
    
    context = {
        'chapter': chapter,
        'class_subject': chapter.class_subject,
    }
    
    return render(request, 'teachers/program/delete_chapter.html', context)

# Vues pour gérer les sous-titres
@login_required
def teacher_create_subtitle(request, chapter_pk):
    """
    Vue pour créer un nouveau sous-titre pour un chapitre
    """
    teacher = request.user
    chapter = get_object_or_404(ProgramChapter, pk=chapter_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if chapter.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à ajouter des sous-titres à ce chapitre.")
        return redirect('teachers:program', class_subject_pk=chapter.class_subject.pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        order = request.POST.get('order', 1)
        
        # Calculer l'ordre si non spécifié
        if not order:
            last_subtitle = Subtitle.objects.filter(
                chapter=chapter
            ).order_by('-order').first()
            order = (last_subtitle.order + 1) if last_subtitle else 1
        
        Subtitle.objects.create(
            chapter=chapter,
            title=title,
            order=order
        )
        
        messages.success(request, 'Sous-titre ajouté avec succès!')
        return redirect('teachers:program', class_subject_pk=chapter.class_subject.pk)
    
    # Récupérer le dernier ordre pour suggérer le prochain
    last_subtitle = Subtitle.objects.filter(
        chapter=chapter
    ).order_by('-order').first()
    suggested_order = (last_subtitle.order + 1) if last_subtitle else 1
    
    context = {
        'chapter': chapter,
        'class_subject': chapter.class_subject,
        'suggested_order': suggested_order,
    }
    
    return render(request, 'teachers/program/create_subtitle.html', context)

@login_required
def teacher_edit_subtitle(request, subtitle_pk):
    """
    Vue pour modifier un sous-titre
    """
    teacher = request.user
    subtitle = get_object_or_404(Subtitle, pk=subtitle_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if subtitle.chapter.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce sous-titre.")
        return redirect('teachers:program', class_subject_pk=subtitle.chapter.class_subject.pk)
    
    if request.method == 'POST':
        subtitle.title = request.POST.get('title', subtitle.title)
        subtitle.order = request.POST.get('order', subtitle.order)
        
        subtitle.save()
        messages.success(request, 'Sous-titre mis à jour avec succès!')
        return redirect('teachers:program', class_subject_pk=subtitle.chapter.class_subject.pk)
    
    context = {
        'subtitle': subtitle,
        'chapter': subtitle.chapter,
        'class_subject': subtitle.chapter.class_subject,
    }
    
    return render(request, 'teachers/program/edit_subtitle.html', context)

@login_required
def teacher_delete_subtitle(request, subtitle_pk):
    """
    Vue pour supprimer un sous-titre
    """
    teacher = request.user
    subtitle = get_object_or_404(Subtitle, pk=subtitle_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if subtitle.chapter.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce sous-titre.")
        return redirect('teachers:program', class_subject_pk=subtitle.chapter.class_subject.pk)
    
    if request.method == 'POST':
        chapter_pk = subtitle.chapter.pk
        subtitle.delete()
        messages.success(request, 'Sous-titre supprimé avec succès!')
        return redirect('teachers:program', class_subject_pk=subtitle.chapter.class_subject.pk)
    
    context = {
        'subtitle': subtitle,
        'chapter': subtitle.chapter,
        'class_subject': subtitle.chapter.class_subject,
    }
    
    return render(request, 'teachers/program/delete_subtitle.html', context)



@login_required
def teacher_interrogations(request, class_subject_pk):
    """
    Vue pour lister toutes les interrogations pour une matière spécifique
    """
    teacher = request.user
    class_subject = get_object_or_404(ClassSubject, pk=class_subject_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à ces interrogations.")
        return redirect('teachers:class_detail', pk=class_subject.class_obj.pk)
    
    # Récupérer toutes les interrogations pour cette matière
    interrogations_list = Interrogation.objects.filter(
        class_subject=class_subject
    ).select_related('chapter').order_by('-date')
    
    # Pagination
    paginator = Paginator(interrogations_list, 10)
    page_number = request.GET.get('page')
    interrogations = paginator.get_page(page_number)
    
    context = {
        'class_subject': class_subject,
        'interrogations': interrogations,
    }
    
    return render(request, 'teachers/interrogations/list.html', context)

@login_required
def teacher_create_interrogation(request, class_subject_pk):
    """
    Vue pour créer une nouvelle interrogation
    """
    teacher = request.user
    class_subject = get_object_or_404(ClassSubject, pk=class_subject_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à créer des interrogations pour cette matière.")
        return redirect('teachers:class_detail', pk=class_subject.class_obj.pk)
    
    # Récupérer les chapitres pour cette matière
    chapters = ProgramChapter.objects.filter(
        class_subject=class_subject
    ).order_by('order')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        chapter_id = request.POST.get('chapter')
        subject_pdf = request.FILES.get('subject_pdf')
        total_points = request.POST.get('total_points', 20)
        
        chapter = None
        if chapter_id:
            chapter = get_object_or_404(ProgramChapter, pk=chapter_id)
        
        interrogation = Interrogation.objects.create(
            class_subject=class_subject,
            chapter=chapter,
            title=title,
            description=description,
            date=date,
            subject_pdf=subject_pdf,
            total_points=total_points
        )
        
        messages.success(request, 'Interrogation créée avec succès!')
        return redirect('teachers:interrogation_detail', pk=interrogation.pk)
    
    context = {
        'class_subject': class_subject,
        'chapters': chapters,
    }
    
    return render(request, 'teachers/interrogations/create.html', context)

@login_required
def teacher_interrogation_detail(request, pk):
    """
    Vue pour afficher les détails d'une interrogation et gérer les notes
    """
    teacher = request.user
    interrogation = get_object_or_404(Interrogation, pk=pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if interrogation.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette interrogation.")
        return redirect('teachers:class_detail', pk=interrogation.class_subject.class_obj.pk)
    
    # Récupérer les élèves inscrits dans la classe
    inscriptions = Inscription.objects.filter(
        classe_demandee=interrogation.class_subject.class_obj,
        annee_scolaire=interrogation.class_subject.school_year
    ).select_related('eleve')
    
    # Créer un dictionnaire des notes existantes pour un accès facile
    existing_grades = {}
    
    # Récupérer les notes pour chaque élève inscrit
    for inscription in inscriptions:
        try:
            grade = InterrogationGrade.objects.get(
                interrogation=interrogation,
                student=inscription.eleve
            )
            existing_grades[inscription.eleve.id] = grade
        except InterrogationGrade.DoesNotExist:
            # L'élève n'a pas encore de note pour cette interrogation
            pass
    
    context = {
        'interrogation': interrogation,
        'inscriptions': inscriptions,
        'existing_grades': existing_grades,
    }
    
    return render(request, 'teachers/interrogations/detail.html', context)

@login_required
def teacher_edit_interrogation(request, pk):
    """
    Vue pour modifier une interrogation
    """
    teacher = request.user
    interrogation = get_object_or_404(Interrogation, pk=pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if interrogation.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette interrogation.")
        return redirect('teachers:class_detail', pk=interrogation.class_subject.class_obj.pk)
    
    # Récupérer les chapitres pour cette matière
    chapters = ProgramChapter.objects.filter(
        class_subject=interrogation.class_subject
    ).order_by('order')
    
    if request.method == 'POST':
        interrogation.title = request.POST.get('title', interrogation.title)
        interrogation.description = request.POST.get('description', interrogation.description)
        interrogation.date = request.POST.get('date', interrogation.date)
        interrogation.total_points = request.POST.get('total_points', interrogation.total_points)
        
        chapter_id = request.POST.get('chapter')
        if chapter_id:
            interrogation.chapter = get_object_or_404(ProgramChapter, pk=chapter_id)
        else:
            interrogation.chapter = None
        
        # Mettre à jour le PDF si un nouveau fichier est fourni
        if request.FILES.get('subject_pdf'):
            interrogation.subject_pdf = request.FILES.get('subject_pdf')
        
        interrogation.save()
        messages.success(request, 'Interrogation mise à jour avec succès!')
        return redirect('teachers:interrogation_detail', pk=interrogation.pk)
    
    context = {
        'interrogation': interrogation,
        'chapters': chapters,
    }
    
    return render(request, 'teachers/interrogations/edit.html', context)

@login_required
def teacher_delete_interrogation(request, pk):
    """
    Vue pour supprimer une interrogation
    """
    teacher = request.user
    interrogation = get_object_or_404(Interrogation, pk=pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if interrogation.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette interrogation.")
        return redirect('teachers:class_detail', pk=interrogation.class_subject.class_obj.pk)
    
    if request.method == 'POST':
        class_subject_pk = interrogation.class_subject.pk
        interrogation.delete()
        messages.success(request, 'Interrogation supprimée avec succès!')
        return redirect('teachers:interrogations', class_subject_pk=class_subject_pk)
    
    context = {
        'interrogation': interrogation,
    }
    
    return render(request, 'teachers/interrogations/delete.html', context)

@login_required
def teacher_save_grades(request, interrogation_pk):
    """
    Vue pour enregistrer les notes des élèves pour une interrogation
    """
    teacher = request.user
    interrogation = get_object_or_404(Interrogation, pk=interrogation_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if interrogation.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à enregistrer des notes pour cette interrogation.")
        return redirect('teachers:class_detail', pk=interrogation.class_subject.class_obj.pk)
    
    if request.method == 'POST':
        # Récupérer les élèves inscrits dans la classe
        inscriptions = Inscription.objects.filter(
            classe_demandee=interrogation.class_subject.class_obj,
            annee_scolaire=interrogation.class_subject.school_year
        )
        
        # Compteurs pour le suivi
        updated_count = 0
        created_count = 0
        skipped_count = 0
        
        # Traiter les notes soumises
        for inscription in inscriptions:
            student_id = inscription.eleve.id
            points_earned = request.POST.get(f'points_{student_id}')
            comments = request.POST.get(f'comments_{student_id}', '')
            
            # Vérifier si une note a été saisie
            if points_earned is not None and points_earned != '':
                try:
                    points_value = float(points_earned)
                    
                    # Vérifier que la note est dans la plage valide
                    if 0 <= points_value <= interrogation.total_points:
                        # Mettre à jour ou créer la note
                        grade, created = InterrogationGrade.objects.update_or_create(
                            interrogation=interrogation,
                            student=inscription.eleve,
                            defaults={
                                'points_earned': points_value,
                                'comments': comments
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    else:
                        # Note hors plage
                        messages.warning(request, f"Note pour {inscription.eleve.get_full_name()} hors plage (0-{interrogation.total_points}).")
                except ValueError:
                    # Valeur non numérique
                    messages.warning(request, f"Note non valide pour {inscription.eleve.get_full_name()}.")
            else:
                skipped_count += 1
        
        # Messages de succès
        if created_count > 0 or updated_count > 0:
            if created_count > 0 and updated_count > 0:
                messages.success(request, f'{created_count} note(s) créée(s) et {updated_count} note(s) mise(s) à jour avec succès!')
            elif created_count > 0:
                messages.success(request, f'{created_count} note(s) créée(s) avec succès!')
            else:
                messages.success(request, f'{updated_count} note(s) mise(s) à jour avec succès!')
            
            if skipped_count > 0:
                messages.info(request, f'{skipped_count} élève(s) sans note (champs laissés vides).')
        else:
            messages.warning(request, 'Aucune note n\'a été enregistrée. Veuillez vérifier que vous avez saisi des notes valides.')
    
    # Rediriger vers la page de détail de l'interrogation
    return redirect('teachers:interrogation_detail', pk=interrogation_pk)


@login_required
def teacher_delete_grade(request, interrogation_pk, student_id):
    """
    Vue pour supprimer la note d'un élève pour une interrogation
    """
    teacher = request.user
    interrogation = get_object_or_404(Interrogation, pk=interrogation_pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if interrogation.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette note.")
        return redirect('teachers:interrogation_detail', pk=interrogation_pk)
    
    # Supprimer la note si elle existe
    deleted_count, _ = InterrogationGrade.objects.filter(
        interrogation=interrogation,
        student_id=student_id
    ).delete()
    
    if deleted_count > 0:
        messages.success(request, 'Note supprimée avec succès!')
    else:
        messages.warning(request, 'Aucune note trouvée pour cet élève.')
    
    return redirect('teachers:interrogation_detail', pk=interrogation_pk)


@login_required
def teacher_interrogation_stats(request, pk):
    """
    Vue pour afficher les statistiques des notes d'une interrogation
    """
    teacher = request.user
    interrogation = get_object_or_404(Interrogation, pk=pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if interrogation.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à accéder aux statistiques de cette interrogation.")
        return redirect('teachers:class_detail', pk=interrogation.class_subject.class_obj.pk)
    
    # Récupérer toutes les notes pour cette interrogation
    grades = InterrogationGrade.objects.filter(
        interrogation=interrogation
    ).select_related('student')
    
    # Calculer les statistiques
    stats = {
        'total_students': grades.count(),
        'average': 0,
        'max': 0,
        'min': 0,
        'success_rate': 0,
        'distribution': {
            'excellent': 0,  # >= 80%
            'good': 0,       # >= 60%
            'fair': 0,       # >= 40%
            'poor': 0        # < 40%
        }
    }
    
    if grades:
        points = [grade.points_earned for grade in grades]
        percentages = [grade.percentage for grade in grades]
        
        stats['average'] = sum(points) / len(points)
        stats['max'] = max(points)
        stats['min'] = min(points)
        stats['success_rate'] = sum(1 for p in percentages if p >= 60) / len(percentages) * 100
        
        for p in percentages:
            if p >= 80:
                stats['distribution']['excellent'] += 1
            elif p >= 60:
                stats['distribution']['good'] += 1
            elif p >= 40:
                stats['distribution']['fair'] += 1
            else:
                stats['distribution']['poor'] += 1
    
    context = {
        'interrogation': interrogation,
        'stats': stats,
        'grades': grades,
    }
    
    return render(request, 'teachers/interrogations/stats.html', context)


@login_required
def teacher_interrogation_export_pdf(request, pk):
    """
    Vue pour exporter les notes d'une interrogation en PDF
    """
    teacher = request.user
    interrogation = get_object_or_404(Interrogation, pk=pk)
    
    # Vérifier que le professeur enseigne bien cette matière dans cette classe
    if interrogation.class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à exporter cette interrogation.")
        return redirect('teachers:class_detail', pk=interrogation.class_subject.class_obj.pk)
    
    # Récupérer les notes des élèves triées par ordre décroissant
    grades = InterrogationGrade.objects.filter(
        interrogation=interrogation
    ).select_related('student').order_by('-points_earned')
    
    # Créer un buffer pour le PDF
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Créer un conteneur pour les éléments
    elements = []
    
    # Définir les styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    ))
    
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    ))
    
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        textColor=colors.HexColor('#2c3e50')
    ))
    
    # Ajouter le logo si disponible
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*inch, height=0.75*inch)
        elements.append(logo)
        elements.append(Spacer(1, 0.5*inch))
    
    # Titre du document
    elements.append(Paragraph("RÉSULTATS D'INTERROGATION", styles['CustomTitle']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Informations sur l'interrogation
    info_data = [
        ['Matière:', interrogation.class_subject.subject.name],
        ['Classe:', interrogation.class_subject.class_obj.name],
        ['Titre:', interrogation.title],
        ['Date:', interrogation.date.strftime('%d/%m/%Y')],
        ['Total des points:', str(interrogation.total_points)],
    ]
    
    if interrogation.chapter:
        info_data.append(['Chapitre:', interrogation.chapter.title])
    
    if interrogation.description:
        info_data.append(['Description:', interrogation.description])
    
    info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#bdc3c7')),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # En-tête du tableau des notes
    headers = ['#', 'Nom & Prénom', 'Note', 'Pourcentage', 'Appréciation', 'Commentaires']
    
    # Préparer les données du tableau
    table_data = [headers]
    
    # Ajouter les lignes de données
    for i, grade in enumerate(grades, 1):
        # Calculer le pourcentage
        percentage = (grade.points_earned / interrogation.total_points) * 100 if interrogation.total_points > 0 else 0
        
        # Déterminer l'appréciation en fonction du pourcentage
        if percentage >= 90:
            appreciation = "Excellent"
            color = colors.HexColor('#27ae60')  # Vert
        elif percentage >= 80:
            appreciation = "Très Bien"
            color = colors.HexColor('#2ecc71')  # Vert clair
        elif percentage >= 70:
            appreciation = "Bien"
            color = colors.HexColor('#3498db')  # Bleu
        elif percentage >= 60:
            appreciation = "Assez Bien"
            color = colors.HexColor('#f39c12')  # Orange
        elif percentage >= 50:
            appreciation = "Passable"
            color = colors.HexColor('#e67e22')  # Orange foncé
        else:
            appreciation = "Insuffisant"
            color = colors.HexColor('#e74c3c')  # Rouge
        
        row = [
            str(i),
            grade.student.get_full_name() or grade.student.username,
            f"{grade.points_earned} / {interrogation.total_points}",
            f"{percentage:.1f}%",
            appreciation,
            grade.comments or "-"
        ]
        
        table_data.append(row)
    
    # Créer le tableau
    table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
    
    # Style du tableau
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    # Ajouter des couleurs pour les appréciations
    for i in range(1, len(table_data)):
        percentage = float(table_data[i][3].replace('%', ''))
        if percentage >= 90:
            table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#27ae60'))]))
        elif percentage >= 80:
            table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#2ecc71'))]))
        elif percentage >= 70:
            table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#3498db'))]))
        elif percentage >= 60:
            table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#f39c12'))]))
        elif percentage >= 50:
            table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#e67e22'))]))
        else:
            table.setStyle(TableStyle([('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#e74c3c'))]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Pied de page
    footer_text = f"Document généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')} par {teacher.get_full_name() or teacher.username}"
    elements.append(Paragraph(footer_text, styles['CustomBody']))
    
    # Générer le PDF
    doc.build(elements)
    
    # Positionner le buffer au début
    buffer.seek(0)
    
    # Créer la réponse HTTP avec le PDF
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="notes_{interrogation.class_subject.class_obj.name}_{interrogation.class_subject.subject.name}_{interrogation.date.strftime("%Y%m%d")}.pdf"'
    
    return response






@login_required
def teacher_textbook_create(request):
    teacher = request.user
    
    # Récupérer les classes où le professeur enseigne
    teacher_classes = ClassSubject.objects.filter(
        teacher=teacher
    ).select_related('class_obj', 'subject')
    
    # Récupérer la classe pré-sélectionnée si elle existe
    preselected_class = None
    students_for_preselected_class = []
    class_subject_id = request.GET.get('class_subject')
    if class_subject_id:
        try:
            preselected_class = ClassSubject.objects.get(pk=class_subject_id, teacher=teacher)
            inscriptions = Inscription.objects.filter(
                classe_demandee=preselected_class.class_obj,
                annee_scolaire=preselected_class.school_year
            ).select_related('eleve').order_by('eleve__last_name', 'eleve__first_name')
            students_for_preselected_class = [inscription.eleve for inscription in inscriptions]
        except ClassSubject.DoesNotExist:
            pass

    if request.method == 'POST':
        # --- DÉBOGAGE : Afficher toutes les données reçues du formulaire ---
        print("\n--- DONNÉES POST REÇUES ---")
        for key, value in request.POST.items():
            print(f"{key}: {value}")
        print("---------------------------\n")

        try:
            with transaction.atomic():
                class_subject_id = request.POST.get('class_subject')
                content = request.POST.get('content')

                if not class_subject_id or not content:
                    messages.error(request, "Veuillez remplir tous les champs obligatoires.")
                    # ... (contexte pour réafficher le formulaire) ...
                    return render(request, 'teachers/textbook/create.html', {
                        'teacher_classes': teacher_classes,
                        'preselected_class': preselected_class,
                        'students': students_for_preselected_class,
                        'attendance_statuses': AttendanceStatus.choices,
                    })

                class_subject = get_object_or_404(ClassSubject, pk=class_subject_id)
                if class_subject.teacher != teacher:
                    messages.error(request, "Vous n'êtes pas autorisé à créer une entrée pour cette classe.")
                    return redirect('teachers:textbook_list')
                
                textbook = Textbook.objects.create(
                    teacher=teacher,
                    class_subject=class_subject,
                    content=content,
                    date=timezone.now().date()
                )
                
                inscriptions = Inscription.objects.filter(
                    classe_demandee=class_subject.class_obj,
                    annee_scolaire=class_subject.school_year
                ).select_related('eleve')

                if not inscriptions.exists():
                    messages.warning(request, "Aucun élève n'est inscrit dans cette classe.")
                else:
                    attendance_records_to_create = []
                    for inscription in inscriptions:
                        student = inscription.eleve
                        student_id = student.id
                        
                        # --- DÉBOGAGE : Vérifier ce qui est récupéré pour chaque élève ---
                        raw_status_from_post = request.POST.get(f'attendance_{student_id}')
                        print(f"Élève ID {student_id} ({student.username}): Statut brut reçu = '{raw_status_from_post}'")
                        
                        # Déterminer le statut de manière robuste
                        if raw_status_from_post == 'ABSENT':
                            final_status = AttendanceStatus.ABSENT
                        elif raw_status_from_post == 'LATE':
                            final_status = AttendanceStatus.LATE
                        elif raw_status_from_post == 'PRESENT':
                            final_status = AttendanceStatus.PRESENT
                        else:
                            # Si rien n'est coché (ne devrait pas arriver avec des radios)
                            # ou si la valeur est inattendue, on peut choisir une valeur par défaut
                            # ou lever une erreur. Ici, on met "Présent" par défaut.
                            final_status = AttendanceStatus.PRESENT
                            print(f"ATTENTION: Statut non reconnu pour l'élève {student_id}, mise par défaut sur 'PRESENT'.")

                        comments = request.POST.get(f'attendance_comments_{student_id}', '')
                        
                        print(f"Élève ID {student_id}: Statut final qui sera sauvegardé = '{final_status}'")
                        
                        attendance_records_to_create.append(
                            Attendance(
                                textbook_entry=textbook,
                                student=student,
                                status=final_status, # On utilise la variable finale
                                comments=comments
                            )
                        )
                    
                    Attendance.objects.bulk_create(attendance_records_to_create)
                    print(f"\n{len(attendance_records_to_create)} enregistrements de présence créés.")

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Entrée ajoutée avec succès!',
                        'textbook_id': textbook.id,
                        'redirect_url': reverse('teachers:textbook_subject', kwargs={'class_subject_pk': class_subject.pk})
                    })
                
                messages.success(request, 'Entrée ajoutée au cahier de texte avec les présences!')
                return redirect('teachers:textbook_subject', class_subject_pk=class_subject.pk)

        except Exception as e:
            print(f"ERREUR LORS DE LA CRÉATION: {e}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': f"Une erreur est survenue : {str(e)}"}, status=500)
            messages.error(request, f"Une erreur est survenue : {str(e)}")
            return render(request, 'teachers/textbook/create.html', {
                'teacher_classes': teacher_classes,
                'preselected_class': preselected_class,
                'students': students_for_preselected_class,
                'attendance_statuses': AttendanceStatus.choices,
            })

    # Pour une requête GET
    context = {
        'teacher_classes': teacher_classes,
        'preselected_class': preselected_class,
        'students': students_for_preselected_class,
        'attendance_statuses': AttendanceStatus.choices,
    }
    return render(request, 'teachers/textbook/create.html', context)


@login_required
def teacher_textbook_detail(request, pk):
    """
    Vue pour afficher les détails d'une entrée du cahier de texte
    """
    teacher = request.user
    textbook = get_object_or_404(Textbook, pk=pk)
    
    # Vérifier que le professeur est bien l'auteur de cette entrée
    if textbook.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à voir cette entrée.")
        return redirect('teachers:textbook_list')
    
    context = {
        'textbook': textbook,
    }
    
    return render(request, 'teachers/textbook/detail.html', context)

@login_required
def teacher_textbook_edit(request, pk):
    """
    Vue pour modifier une entrée du cahier de texte avec les présences
    """
    teacher = request.user
    textbook = get_object_or_404(Textbook, pk=pk)
    
    # Vérifier que le professeur est bien l'auteur de cette entrée
    if textbook.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette entrée.")
        return redirect('teachers:textbook_subject', class_subject_pk=textbook.class_subject.pk)
    
    # Récupérer les classes où le professeur enseigne
    teacher_classes = ClassSubject.objects.filter(
        teacher=teacher
    ).select_related('class_obj', 'subject')
    
    # Récupérer les présences existantes
    attendances = textbook.attendances.all()
    
    if request.method == 'POST':
        class_subject_id = request.POST.get('class_subject')
        content = request.POST.get('content')
        
        class_subject = get_object_or_404(ClassSubject, pk=class_subject_id)
        
        # Vérifier que le professeur enseigne bien dans cette classe
        if class_subject.teacher != teacher:
            messages.error(request, "Vous n'êtes pas autorisé à modifier cette entrée pour cette classe.")
            return redirect('teachers:textbook_subject', class_subject_pk=textbook.class_subject.pk)
        
        # Mettre à jour l'entrée du cahier de texte
        textbook.class_subject = class_subject
        textbook.content = content
        textbook.save()
        
        # Mettre à jour les présences
        for attendance in attendances:
            student_id = attendance.student.id
            status_key = f'attendance_{student_id}'
            comments_key = f'attendance_comments_{student_id}'
            
            # Récupérer le statut depuis le formulaire
            status = request.POST.get(status_key, AttendanceStatus.PRESENT)
            comments = request.POST.get(comments_key, '')
            
            # S'assurer que le statut est valide
            if status not in [choice[0] for choice in AttendanceStatus.choices]:
                status = AttendanceStatus.PRESENT
            
            # Mettre à jour l'enregistrement de présence
            attendance.status = status
            attendance.comments = comments
            attendance.save()
            
            # Pour le débogage - imprimer les valeurs reçues
            print(f"Élève: {attendance.student.username}, Statut: {status}, Commentaires: {comments}")
        
        messages.success(request, 'Entrée du cahier de texte et présences mises à jour avec succès!')
        return redirect('teachers:textbook_subject', class_subject_pk=textbook.class_subject.pk)
    
    context = {
        'textbook': textbook,
        'teacher_classes': teacher_classes,
        'attendances': attendances,
        'attendance_statuses': AttendanceStatus.choices,
    }
    
    return render(request, 'teachers/textbook/edit.html', context)


@login_required
def teacher_textbook_subject(request, class_subject_pk):
    """
    Vue pour afficher le cahier de texte pour une matière spécifique.
    
    Fonctionnalités :
    - Vérifie les permissions de l'utilisateur.
    - Affiche les entrées triées de la plus récente à la plus ancienne.
    - Gère la pagination (10 entrées par page).
    - Optimise les performances avec prefetch_related.
    """
    teacher = request.user
    class_subject = get_object_or_404(ClassSubject, pk=class_subject_pk)
    
    if class_subject.teacher != teacher:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à ce cahier de texte.")
        return redirect('teachers:class_detail', pk=class_subject.class_obj.pk)
    
    textbook_entries = Textbook.objects.filter(
        teacher=teacher,
        class_subject=class_subject
    ).prefetch_related('attendances').order_by('-date') 
    
    paginator = Paginator(textbook_entries, 5)

    page_number = request.GET.get('page')
    entries = paginator.get_page(page_number)
    
    context = {
        'class_subject': class_subject,
        'entries': entries,  
    }
    

    return render(request, 'teachers/textbook/subject.html', context)





@login_required
@csrf_exempt
def get_students_by_class(request):
    """
    Vue API pour récupérer les élèves d'une classe spécifique
    """
    class_subject_id = request.GET.get('class_subject')
    
    if not class_subject_id:
        return JsonResponse({'error': 'Paramètre class_subject manquant'}, status=400)
    
    try:
        class_subject = ClassSubject.objects.get(pk=class_subject_id, teacher=request.user)
    except ClassSubject.DoesNotExist:
        return JsonResponse({'error': 'Classe non trouvée ou non autorisée'}, status=404)
    
    # Récupérer les élèves inscrits dans la classe
    inscriptions = Inscription.objects.filter(
        classe_demandee=class_subject.class_obj,
        annee_scolaire=class_subject.school_year
    ).select_related('eleve')
    
    students = []
    for inscription in inscriptions:
        students.append({
            'id': inscription.eleve.id,
            'username': inscription.eleve.username,
            'full_name': inscription.eleve.get_full_name()
        })
    
    return JsonResponse({'students': students})



@login_required
def api_textbook_detail(request, pk):
    """
    Vue API pour récupérer les détails d'un cahier de texte au format JSON
    """
    textbook = get_object_or_404(Textbook, pk=pk)
    
    # Récupérer les présences pour ce cahier de texte
    attendances = textbook.attendances.select_related('student')
    
    attendance_data = []
    for attendance in attendances:
        attendance_data.append({
            'student_name': attendance.student.get_full_name() or attendance.student.username,
            'status': attendance.status,
            'comments': attendance.comments
        })
    
    data = {
        'success': True,
        'id': textbook.id,
        'date': textbook.date.isoformat(),
        'content': textbook.content,
        'subject': textbook.class_subject.subject.name,
        'teacher': textbook.teacher.get_full_name() or textbook.teacher.username,
        'attendances': attendance_data
    }
    
    return JsonResponse(data)