from django.shortcuts import render

# Create your views here.
# teachers/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.models import User
from academics.models import ClassSubject, ScheduleEntry, Enrollment, Class, Schedule
from school.models import SchoolYear


@login_required
def teacher_dashboard(request):
    """
    Vue pour le tableau de bord du professeur
    """
    teacher = request.user
    
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
    total_students = Enrollment.objects.filter(
        class_obj__class_subjects__teacher=teacher,
        class_obj__class_subjects__school_year=active_school_year
    ).distinct().count()
    
    # Compter le nombre total de cours du professeur
    total_courses = ScheduleEntry.objects.filter(
        class_subject__teacher=teacher,
        schedule__school_year=active_school_year
    ).count()
    
    context = {
        'teacher_classes_count': teacher_classes_count,
        'teacher_subjects_count': teacher_subjects_count,
        'total_students': total_students,
        'total_courses': total_courses,
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
    Vue pour afficher les détails d'une classe spécifique
    """
    teacher = request.user
    class_obj = get_object_or_404(Class, pk=pk)
    
    # Vérifier que le professeur enseigne bien dans cette classe
    if not ClassSubject.objects.filter(teacher=teacher, class_obj=class_obj).exists():
        # Rediriger vers la liste des classes avec un message d'erreur
        from django.contrib import messages
        messages.error(request, "Vous n'êtes pas autorisé à voir cette classe.")
        return redirect('teachers:classes_list')
    
    # Récupérer les matières enseignées par ce professeur dans cette classe
    teacher_subjects = ClassSubject.objects.filter(
        teacher=teacher,
        class_obj=class_obj
    ).select_related('subject')
    
    context = {
        'class_obj': class_obj,
        'teacher_subjects': teacher_subjects,
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
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
    }
    
    return render(request, 'teachers/schedule/list.html', context)