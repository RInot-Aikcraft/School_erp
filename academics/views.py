from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Subject, ClassLevel, Class, Enrollment, Assignment, Grade
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from school.models import SchoolYear
from .models import Subject, ClassLevel, Class, Enrollment, Assignment, Grade, ClassSubject, Schedule, ScheduleEntry, TimeSlot
from django.db.models import Prefetch
from django.http import JsonResponse

def is_admin(user):
    return user.is_authenticated and user.userprofile.user_type == 'admin'

def is_teacher(user):
    return user.is_authenticated and user.userprofile.user_type == 'teacher'

# Vues pour la gestion des matières
@login_required
@user_passes_test(is_admin)
def subject_list(request):
    subjects = Subject.objects.all().order_by('name')
    return render(request, 'academics/subject_list.html', {'subjects': subjects})

@login_required
@user_passes_test(is_admin)
def subject_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        
        Subject.objects.create(
            name=name,
            code=code,
            description=description
        )
        
        messages.success(request, 'Matière créée avec succès!')
        return redirect('academics:subject_list')
    
    return render(request, 'academics/subject_form.html')

@login_required
@user_passes_test(is_admin)
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    return render(request, 'academics/subject_detail.html', {'subject': subject})

@login_required
@user_passes_test(is_admin)
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        subject.name = request.POST.get('name', subject.name)
        subject.code = request.POST.get('code', subject.code)
        subject.description = request.POST.get('description', subject.description)
        
        subject.save()
        messages.success(request, 'Matière mise à jour avec succès!')
        return redirect('academics:subject_list')
    
    return render(request, 'academics/subject_form.html', {'subject': subject})

@login_required
@user_passes_test(is_admin)
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Matière supprimée avec succès!')
        return redirect('academics:subject_list')
    
    return render(request, 'academics/subject_confirm_delete.html', {'subject': subject})

# Vues pour la gestion des classes
@login_required
@user_passes_test(is_admin)
def class_list(request):
    classes = Class.objects.all().order_by('name')
    return render(request, 'academics/class_list.html', {'classes': classes})

@login_required
@user_passes_test(is_admin)
def class_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        level_id = request.POST.get('level')
        school_year_id = request.POST.get('school_year')
        main_teacher_id = request.POST.get('main_teacher')
        max_students = request.POST.get('max_students', 30)
        
        level = get_object_or_404(ClassLevel, pk=level_id)
        school_year = get_object_or_404(SchoolYear, pk=school_year_id)
        
        main_teacher = None
        if main_teacher_id:
            main_teacher = get_object_or_404(User, pk=main_teacher_id)
        
        Class.objects.create(
            name=name,
            level=level,
            school_year=school_year,
            main_teacher=main_teacher,
            max_students=max_students
        )
        
        messages.success(request, 'Classe créée avec succès!')
        return redirect('academics:class_list')
    
    levels = ClassLevel.objects.all()
    school_years = SchoolYear.objects.all()
    teachers = User.objects.filter(userprofile__user_type='teacher')
    
    return render(request, 'academics/class_form.html', {
        'levels': levels,
        'school_years': school_years,
        'teachers': teachers
    })

@login_required
@user_passes_test(is_admin)
def class_detail(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    enrollments = class_obj.enrollments.all()
    
    return render(request, 'academics/class_detail.html', {
        'class_obj': class_obj,
        'enrollments': enrollments
    })

@login_required
@user_passes_test(is_admin)
def class_edit(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        class_obj.name = request.POST.get('name', class_obj.name)
        
        level_id = request.POST.get('level')
        if level_id:
            class_obj.level = get_object_or_404(ClassLevel, pk=level_id)
        
        school_year_id = request.POST.get('school_year')
        if school_year_id:
            class_obj.school_year = get_object_or_404(SchoolYear, pk=school_year_id)
        
        main_teacher_id = request.POST.get('main_teacher')
        if main_teacher_id:
            class_obj.main_teacher = get_object_or_404(User, pk=main_teacher_id)
        else:
            class_obj.main_teacher = None
        
        class_obj.max_students = request.POST.get('max_students', class_obj.max_students)
        
        class_obj.save()
        messages.success(request, 'Classe mise à jour avec succès!')
        return redirect('academics:class_list')
    
    levels = ClassLevel.objects.all()
    school_years = SchoolYear.objects.all()
    teachers = User.objects.filter(userprofile__user_type='teacher')
    
    return render(request, 'academics/class_form.html', {
        'class': class_obj,
        'levels': levels,
        'school_years': school_years,
        'teachers': teachers
    })

@login_required
@user_passes_test(is_admin)
def class_delete(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, 'Classe supprimée avec succès!')
        return redirect('academics:class_list')
    
    return render(request, 'academics/class_confirm_delete.html', {'class': class_obj})

# Vues pour la gestion des devoirs
@login_required
@user_passes_test(is_admin)
def assignment_list(request):
    assignments = Assignment.objects.all().order_by('-due_date')
    return render(request, 'academics/assignment_list.html', {'assignments': assignments})

@login_required
@user_passes_test(is_admin)
def assignment_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        subject_id = request.POST.get('subject')
        teacher_id = request.POST.get('teacher')
        class_id = request.POST.get('class')
        due_date = request.POST.get('due_date')
        total_points = request.POST.get('total_points', 100)
        
        subject = get_object_or_404(Subject, pk=subject_id)
        teacher = get_object_or_404(User, pk=teacher_id)
        class_obj = get_object_or_404(Class, pk=class_id)
        
        Assignment.objects.create(
            title=title,
            description=description,
            subject=subject,
            teacher=teacher,
            class_obj=class_obj,
            due_date=due_date,
            total_points=total_points
        )
        
        messages.success(request, 'Devoir créé avec succès!')
        return redirect('academics:assignment_list')
    
    subjects = Subject.objects.all()
    teachers = User.objects.filter(userprofile__user_type='teacher')
    classes = Class.objects.all()
    
    return render(request, 'academics/assignment_form.html', {
        'subjects': subjects,
        'teachers': teachers,
        'classes': classes
    })

@login_required
@user_passes_test(is_admin)
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    grades = assignment.grades.all()
    
    return render(request, 'academics/assignment_detail.html', {
        'assignment': assignment,
        'grades': grades
    })

@login_required
@user_passes_test(is_admin)
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.method == 'POST':
        assignment.title = request.POST.get('title', assignment.title)
        assignment.description = request.POST.get('description', assignment.description)
        
        subject_id = request.POST.get('subject')
        if subject_id:
            assignment.subject = get_object_or_404(Subject, pk=subject_id)
        
        teacher_id = request.POST.get('teacher')
        if teacher_id:
            assignment.teacher = get_object_or_404(User, pk=teacher_id)
        
        class_id = request.POST.get('class')
        if class_id:
            assignment.class_obj = get_object_or_404(Class, pk=class_id)
        
        assignment.due_date = request.POST.get('due_date', assignment.due_date)
        assignment.total_points = request.POST.get('total_points', assignment.total_points)
        
        assignment.save()
        messages.success(request, 'Devoir mis à jour avec succès!')
        return redirect('academics:assignment_list')
    
    subjects = Subject.objects.all()
    teachers = User.objects.filter(userprofile__user_type='teacher')
    classes = Class.objects.all()
    
    return render(request, 'academics/assignment_form.html', {
        'assignment': assignment,
        'subjects': subjects,
        'teachers': teachers,
        'classes': classes
    })

@login_required
@user_passes_test(is_admin)
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Devoir supprimé avec succès!')
        return redirect('academics:assignment_list')
    
    return render(request, 'academics/assignment_confirm_delete.html', {'assignment': assignment})

# Vues pour la gestion des notes
@login_required
@user_passes_test(is_admin)
def grade_list(request):
    grades = Grade.objects.all().order_by('-graded_at')
    return render(request, 'academics/grade_list.html', {'grades': grades})

@login_required
@user_passes_test(is_admin)
def grade_create(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        assignment_id = request.POST.get('assignment')
        points_earned = request.POST.get('points_earned')
        comments = request.POST.get('comments', '')
        
        student = get_object_or_404(User, pk=student_id)
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        
        Grade.objects.create(
            student=student,
            assignment=assignment,
            points_earned=points_earned,
            comments=comments
        )
        
        messages.success(request, 'Note créée avec succès!')
        return redirect('academics:grade_list')
    
    students = User.objects.filter(userprofile__user_type='student')
    assignments = Assignment.objects.all()
    
    return render(request, 'academics/grade_form.html', {
        'students': students,
        'assignments': assignments
    })

@login_required
@user_passes_test(is_admin)
def grade_detail(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    return render(request, 'academics/grade_detail.html', {'grade': grade})

@login_required
@user_passes_test(is_admin)
def grade_edit(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        assignment_id = request.POST.get('assignment')
        grade.points_earned = request.POST.get('points_earned', grade.points_earned)
        grade.comments = request.POST.get('comments', grade.comments)
        
        if student_id:
            grade.student = get_object_or_404(User, pk=student_id)
        
        if assignment_id:
            grade.assignment = get_object_or_404(Assignment, pk=assignment_id)
        
        grade.save()
        messages.success(request, 'Note mise à jour avec succès!')
        return redirect('academics:grade_list')
    
    students = User.objects.filter(userprofile__user_type='student')
    assignments = Assignment.objects.all()
    
    return render(request, 'academics/grade_form.html', {
        'grade': grade,
        'students': students,
        'assignments': assignments
    })

@login_required
@user_passes_test(is_admin)
def grade_delete(request, pk):
    grade = get_object_or_404(Grade, pk=pk)
    
    if request.method == 'POST':
        grade.delete()
        messages.success(request, 'Note supprimée avec succès!')
        return redirect('academics:grade_list')
    
    return render(request, 'academics/grade_confirm_delete.html', {'grade': grade})

# Vues pour la gestion des niveaux
@login_required
@user_passes_test(is_admin)
def class_level_list(request):
    levels = ClassLevel.objects.all().order_by('name')
    return render(request, 'academics/class_level_list.html', {'levels': levels})

@login_required
@user_passes_test(is_admin)
def class_level_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        ClassLevel.objects.create(
            name=name,
            description=description
        )
        
        messages.success(request, 'Niveau créé avec succès!')
        return redirect('academics:class_level_list')
    
    return render(request, 'academics/class_level_form.html')

@login_required
@user_passes_test(is_admin)
def class_level_detail(request, pk):
    level = get_object_or_404(ClassLevel, pk=pk)
    classes = level.classes.all()
    
    return render(request, 'academics/class_level_detail.html', {
        'level': level,
        'classes': classes
    })

@login_required
@user_passes_test(is_admin)
def class_level_edit(request, pk):
    level = get_object_or_404(ClassLevel, pk=pk)
    
    if request.method == 'POST':
        level.name = request.POST.get('name', level.name)
        level.description = request.POST.get('description', level.description)
        
        level.save()
        messages.success(request, 'Niveau mis à jour avec succès!')
        return redirect('academics:class_level_list')
    
    return render(request, 'academics/class_level_form.html', {'level': level})

@login_required
@user_passes_test(is_admin)
def class_level_delete(request, pk):
    level = get_object_or_404(ClassLevel, pk=pk)
    
    if request.method == 'POST':
        level.delete()
        messages.success(request, 'Niveau supprimé avec succès!')
        return redirect('academics:class_level_list')
    
    return render(request, 'academics/class_level_confirm_delete.html', {'level': level})


@login_required
@user_passes_test(is_admin)
def class_detail(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    enrollments = class_obj.enrollments.all()
    all_subjects = Subject.objects.all()
    teachers = User.objects.filter(userprofile__user_type='teacher')
    assigned_subjects = ClassSubject.objects.filter(
        class_obj=class_obj, 
        school_year=class_obj.school_year
    ).select_related('subject', 'teacher').order_by('subject__name')

    context = {
        'class_obj': class_obj,
        'enrollments': enrollments,
        'all_subjects': all_subjects,
        'teachers': teachers,
        'assigned_subjects': assigned_subjects,
    }
    
    return render(request, 'academics/class_detail.html', context)


# Dans academics/views.py

@login_required
@user_passes_test(is_admin)
def add_subject_to_class(request, class_pk):
    class_obj = get_object_or_404(Class, pk=class_pk)
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        teacher_id = request.POST.get('teacher')
        coefficient = request.POST.get('coefficient', 1) # Récupérer le coefficient
        
        subject = get_object_or_404(Subject, pk=subject_id)
        teacher = get_object_or_404(User, pk=teacher_id)
        
        if not ClassSubject.objects.filter(
            class_obj=class_obj, 
            subject=subject, 
            school_year=class_obj.school_year
        ).exists():
            ClassSubject.objects.create(
                class_obj=class_obj,
                subject=subject,
                teacher=teacher,
                school_year=class_obj.school_year,
                coefficient=coefficient # Sauvegarder le coefficient
            )
            messages.success(request, f"La matière '{subject.name}' a été ajoutée avec succès.")
        else:
            messages.warning(request, f"La matière '{subject.name}' est déjà assignée à cette classe pour cette année scolaire.")
            
        return redirect('academics:class_detail', pk=class_obj.pk)
    
    return redirect('academics:class_detail', pk=class_obj.pk)


@login_required
@user_passes_test(is_admin)
def remove_subject_from_class(request, class_subject_pk):
    class_subject = get_object_or_404(ClassSubject, pk=class_subject_pk)
    class_pk = class_subject.class_obj.pk # On récupère l'ID de la classe pour la redirection
    
    if request.method == 'POST':
        subject_name = class_subject.subject.name
        class_subject.delete()
        messages.success(request, f"La matière '{subject_name}' a été retirée de la classe.")
        return redirect('academics:class_detail', pk=class_pk)
        
    # Si ce n'est pas POST, on pourrait rediriger ou afficher une page de confirmation
    return redirect('academics:class_detail', pk=class_pk)



@login_required
@user_passes_test(is_admin)
def get_teachers_for_subject(request):
    """
    Vue API pour récupérer les enseignants qualifiés pour une matière donnée.
    Retourne une réponse JSON.
    """
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': 'subject_id manquant'}, status=400)

    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Matière non trouvée'}, status=404)

    # Récupérer les User qui sont liés à cette matière via le modèle TeacherSubject
    teachers = User.objects.filter(
        userprofile__user_type='teacher',
        subjects__subject=subject # La magie opère ici !
    ).distinct().order_by('last_name', 'first_name')

    # Formatter les données pour le select2 (ou un simple select)
    teacher_list = [{'id': t.pk, 'text': t.get_full_name() or t.username} for t in teachers]
    
    return JsonResponse({'teachers': teacher_list})


@login_required
@user_passes_test(is_admin)
def class_schedule(request, class_pk):
    class_obj = get_object_or_404(Class, pk=class_pk)
    
    # Récupérer ou créer l'emploi du temps pour cette classe
    schedule, created = Schedule.objects.get_or_create(
        class_obj=class_obj,
        school_year=class_obj.school_year
    )
    
    # Récupérer toutes les entrées d'emploi du temps
    entries = schedule.entries.select_related(
        'class_subject__subject', 
        'class_subject__teacher', 
        'time_slot'
    ).order_by('day_of_week', 'time_slot__start_time')
    
    # Organiser les entrées par jour
    schedule_by_day = {}
    for day_num, day_name in [
        ('1', 'Lundi'), ('2', 'Mardi'), ('3', 'Mercredi'), 
        ('4', 'Jeudi'), ('5', 'Vendredi'), ('6', 'Samedi'), ('7', 'Dimanche')
    ]:
        schedule_by_day[day_num] = {
            'name': day_name,
            'entries': [entry for entry in entries if entry.day_of_week == day_num]
        }
    
    days_of_week = [
        ('1', 'Lundi'), ('2', 'Mardi'), ('3', 'Mercredi'),
        ('4', 'Jeudi'), ('5', 'Vendredi'), ('6', 'Samedi'), ('7', 'Dimanche'),
    ]
    
    context = {
        'class_obj': class_obj,
        'schedule': schedule,
        'schedule_by_day': schedule_by_day,
        'days_of_week': days_of_week,
    }
    
    return render(request, 'academics/class_schedule.html', context)

@login_required
@user_passes_test(is_admin)
def add_schedule_entry(request, schedule_pk):
    schedule = get_object_or_404(Schedule, pk=schedule_pk)
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        # Récupérer le ClassSubject par son ID
        class_subject = get_object_or_404(ClassSubject, pk=subject_id)
        
        # Vérifier que ce ClassSubject appartient bien à la classe du schedule
        if class_subject.class_obj != schedule.class_obj:
            messages.error(request, "Cette matière n'est pas assignée à cette classe.")
            return redirect('academics:class_schedule', class_pk=schedule.class_obj.pk)  # Correction ici
        
        # Créer ou récupérer un TimeSlot correspondant aux heures spécifiées
        time_slot, created = TimeSlot.objects.get_or_create(
            start_time=start_time,
            end_time=end_time
        )
        
        # Vérifier si une entrée n'existe pas déjà à ce moment
        if ScheduleEntry.objects.filter(
            schedule=schedule,
            day_of_week=day_of_week,
            time_slot=time_slot
        ).exists():
            messages.warning(request, "Un cours est déjà programmé à ce moment.")
        else:
            # Créer la nouvelle entrée dans l'emploi du temps
            ScheduleEntry.objects.create(
                schedule=schedule,
                class_subject=class_subject,
                time_slot=time_slot,
                day_of_week=day_of_week
            )
            messages.success(request, "Le cours a été ajouté à l'emploi du temps.")
            
        return redirect('academics:class_schedule', class_pk=schedule.class_obj.pk)  # Correction ici
    
    # Si ce n'est pas POST, rediriger vers la page de l'emploi du temps
    return redirect('academics:class_schedule', class_pk=schedule.class_obj.pk)  # Correction ici