from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, ParentStudentRelationship
from .forms import CustomUserCreationForm, ParentCreationForm, StudentCreationForm, ParentStudentRelationshipForm
from academics.models import Subject, TeacherSubject, TeacherSubjectLevel, ClassLevel, Class, Assignment, Enrollment
from django.db.models import Count
from school.models import SchoolYear


def is_admin(user):
    return user.is_authenticated and user.userprofile.user_type == 'admin'

def is_teacher(user):
    return user.is_authenticated and user.userprofile.user_type == 'teacher'

def is_student(user):
    return user.is_authenticated and user.userprofile.user_type == 'student'

def is_parent(user):
    return user.is_authenticated and user.userprofile.user_type == 'parent'

def redirect_to_login(request):
    if request.user.is_authenticated:
        # Redirection en fonction du type d'utilisateur
        if request.user.userprofile.user_type == 'admin':
            return redirect('auth_app:admin_dashboard')
        elif request.user.userprofile.user_type == 'teacher':
            return redirect('teachers:dashboard')
        elif request.user.userprofile.user_type == 'student':
            return redirect('auth_app:student_dashboard')
        elif request.user.userprofile.user_type == 'parent':
            return redirect('auth_app:parent_dashboard')
    else:
        return redirect('auth_app:login')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = User.objects.count()
    admin_count = UserProfile.objects.filter(user_type='admin').count()
    teacher_count = UserProfile.objects.filter(user_type='teacher').count()
    student_count = UserProfile.objects.filter(user_type='student').count()
    parent_count = UserProfile.objects.filter(user_type='parent').count()
    
    # Récupérer l'année scolaire en cours
    current_school_year = SchoolYear.objects.filter(current=True).first()
    
    context_data = {
        'total_users': total_users,
        'admin_count': admin_count,
        'teacher_count': teacher_count,
        'student_count': student_count,
        'parent_count': parent_count,
        'users': User.objects.all().order_by('-date_joined')[:5],
        'current_school_year': current_school_year,
    }
    
    if current_school_year:
        # Nombre de classes cette année
        class_count = Class.objects.filter(school_year=current_school_year).count()
        
        # Nombre de matières enseignées (on compte les TeacherSubject uniques)
        subject_count = Subject.objects.filter(teachers__isnull=False).distinct().count()
        
        # Nombre d'élèves inscrits cette année
        enrollment_count = Enrollment.objects.filter(school_year=current_school_year, is_active=True).count()
        
        # Prochains devoirs à rendre (à partir d'aujourd'hui)
        from django.utils import timezone
        upcoming_assignments = Assignment.objects.filter(
            due_date__gte=timezone.now()
        ).order_by('due_date')[:5]
        
        context_data.update({
            'class_count': class_count,
            'subject_count': subject_count,
            'enrollment_count': enrollment_count,
            'upcoming_assignments': upcoming_assignments,
        })
    else:
        # Si aucune année n'est définie, on met des valeurs nulles ou des messages
        context_data.update({
            'class_count': 0,
            'subject_count': 0,
            'enrollment_count': 0,
            'upcoming_assignments': [],
        })
    
    return render(request, 'auth_app/admin/dashboard.html', context_data)

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()
    return render(request, 'auth_app/admin/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé avec succès!')
            return redirect('auth_app:user_list')
        else:
            # Afficher les erreurs du formulaire pour le débogage
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth_app/admin/user_form.html', {'form': form, 'title': 'Créer un utilisateur'})

@login_required
@user_passes_test(is_admin)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.userprofile
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        profile.user_type = request.POST.get('user_type', 'student')
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        
        if request.POST.get('date_of_birth'):
            profile.date_of_birth = request.POST.get('date_of_birth')
        
        user.save()
        profile.save()
        
        messages.success(request, 'Utilisateur mis à jour avec succès!')
        return redirect('auth_app:user_list')
    
    context = {
        'user': user,
        'profile': profile,
        'title': 'Modifier un utilisateur',
        'user_types': UserProfile.USER_TYPES
    }
    return render(request, 'auth_app/admin/user_form.html', context)

@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Utilisateur supprimé avec succès!')
        return redirect('auth_app:user_list')
    return render(request, 'auth_app/admin/user_confirm_delete.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'auth_app/admin/user_detail.html', {'user': user})

# Vues pour les autres types d'utilisateurs (implémentation de base)
@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    return redirect('teachers:dashboard')

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    return render(request, 'auth_app/student/dashboard.html')

@login_required
@user_passes_test(is_parent)
def parent_dashboard(request):
    return render(request, 'auth_app/parent/dashboard.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirection en fonction du type d'utilisateur
            if user.userprofile.user_type == 'admin':
                return redirect('auth_app:admin_dashboard')
            elif user.userprofile.user_type == 'teacher':
                return redirect('teachers:dashboard')
            elif user.userprofile.user_type == 'student':
                return redirect('auth_app:student_dashboard')
            elif user.userprofile.user_type == 'parent':
                return redirect('auth_app:parent_dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'auth_app/login.html')

def custom_logout(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('auth_app:login')

# Vues pour la gestion des enseignants
@login_required
@user_passes_test(is_admin)
def teacher_list(request):
    teachers = User.objects.filter(userprofile__user_type='teacher')
    return render(request, 'auth_app/admin/teacher_list.html', {'teachers': teachers})

@login_required
@user_passes_test(is_admin)
def teacher_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Ajout des matières enseignées
            subject_ids = request.POST.getlist('subjects')
            for subject_id in subject_ids:
                subject = get_object_or_404(Subject, pk=subject_id)
                teacher_subject = TeacherSubject.objects.create(teacher=user, subject=subject)
                
                # Ajout des niveaux pour chaque matière
                level_ids = request.POST.getlist(f'levels_{subject_id}')
                for level_id in level_ids:
                    class_level = get_object_or_404(ClassLevel, pk=level_id)
                    TeacherSubjectLevel.objects.create(teacher_subject=teacher_subject, class_level=class_level)
            
            messages.success(request, 'Enseignant créé avec succès!')
            return redirect('auth_app:teacher_list')
        else:
            # Afficher les erreurs du formulaire pour le débogage
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    subjects = Subject.objects.all()
    class_levels = ClassLevel.objects.all()
    
    return render(request, 'auth_app/admin/teacher_form.html', {
        'form': form, 
        'title': 'Créer un enseignant',
        'subjects': subjects,
        'class_levels': class_levels,
        'teacher_subject_ids': []
    })

@login_required
@user_passes_test(is_admin)
def teacher_edit(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    profile = teacher.userprofile
    
    if request.method == 'POST':
        # Mise à jour des informations de base
        teacher.first_name = request.POST.get('first_name', '')
        teacher.last_name = request.POST.get('last_name', '')
        teacher.email = request.POST.get('email', '')
        
        # Mise à jour des informations du profil
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        
        if request.POST.get('date_of_birth'):
            profile.date_of_birth = request.POST.get('date_of_birth')
            
        # Informations personnelles supplémentaires
        profile.gender = request.POST.get('gender', '')
        profile.place_of_birth = request.POST.get('place_of_birth', '')
        profile.nationality = request.POST.get('nationality', '')
        profile.id_card_number = request.POST.get('id_card_number', '')
        profile.civil_status = request.POST.get('civil_status', '')
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        
        # Informations professionnelles
        profile.internal_id = request.POST.get('internal_id', '')
        profile.professional_id = request.POST.get('professional_id', '')
        profile.diplomas = request.POST.get('diplomas', '')
        
        if request.POST.get('hire_date'):
            profile.hire_date = request.POST.get('hire_date')
            
        profile.position = request.POST.get('position', '')
        profile.employment_status = request.POST.get('employment_status', '')
        
        if request.POST.get('experience_years'):
            profile.experience_years = int(request.POST.get('experience_years'))
            
        profile.previous_positions = request.POST.get('previous_positions', '')
        
        # Sauvegarde
        teacher.save()
        profile.save()
        
        # Mise à jour des matières enseignées
        TeacherSubject.objects.filter(teacher=teacher).delete()
        subject_ids = request.POST.getlist('subjects')
        
        for subject_id in subject_ids:
            subject = get_object_or_404(Subject, pk=subject_id)
            teacher_subject = TeacherSubject.objects.create(teacher=teacher, subject=subject)
            
            # Ajout des niveaux pour chaque matière
            level_ids = request.POST.getlist(f'levels_{subject_id}')
            for level_id in level_ids:
                class_level = get_object_or_404(ClassLevel, pk=level_id)
                TeacherSubjectLevel.objects.create(teacher_subject=teacher_subject, class_level=class_level)
        
        # Gestion de la photo de profil
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
        
        messages.success(request, 'Enseignant mis à jour avec succès!')
        return redirect('auth_app:teacher_list')
    
    # Prétraitement des données pour le template
    teacher_subjects = TeacherSubject.objects.filter(teacher=teacher)
    teacher_subject_ids = [ts.subject.pk for ts in teacher_subjects]
    
    # Préparation des niveaux par matière
    subjects_levels = {}
    for teacher_subject in teacher_subjects:
        levels = TeacherSubjectLevel.objects.filter(teacher_subject=teacher_subject)
        subjects_levels[teacher_subject.subject.pk] = [level.class_level.pk for level in levels]
    
    subjects = Subject.objects.all()
    class_levels = ClassLevel.objects.all()
    
    context = {
        'teacher': teacher,
        'profile': profile,
        'title': 'Modifier un enseignant',
        'teacher_subjects': teacher_subjects,
        'teacher_subject_ids': teacher_subject_ids,
        'subjects': subjects,
        'class_levels': class_levels,
        'subjects_levels': subjects_levels
    }
    return render(request, 'auth_app/admin/teacher_form.html', context)

@login_required
@user_passes_test(is_admin)
def teacher_detail(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    teacher_subjects = TeacherSubject.objects.filter(teacher=teacher).prefetch_related('levels')
    return render(request, 'auth_app/admin/teacher_detail.html', {
        'teacher': teacher,
        'teacher_subjects': teacher_subjects
    })

@login_required
@user_passes_test(is_admin)
def teacher_delete(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Enseignant supprimé avec succès!')
        return redirect('auth_app:teacher_list')
    return render(request, 'auth_app/admin/teacher_confirm_delete.html', {'teacher': teacher})

# Vues pour la gestion des parents
@login_required
@user_passes_test(is_admin)
def parent_list(request):
    parents = User.objects.filter(userprofile__user_type='parent')
    return render(request, 'auth_app/admin/parent_list.html', {'parents': parents})

@login_required
@user_passes_test(is_admin)
def parent_create(request):
    if request.method == 'POST':
        form = ParentCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Le formulaire s'occupe déjà de tout, plus besoin de mettre à jour manuellement
            messages.success(request, 'Parent créé avec succès!')
            return redirect('auth_app:parent_list')
        else:
            # Afficher les erreurs du formulaire pour le débogage
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Utiliser le formulaire spécifique pour les parents
        form = ParentCreationForm()
    
    return render(request, 'auth_app/admin/parent_form.html', {
        'form': form, 
        'title': 'Créer un parent'
    })

@login_required
@user_passes_test(is_admin)
def parent_edit(request, pk):
    parent = get_object_or_404(User, pk=pk)
    profile = parent.userprofile
    
    if request.method == 'POST':
        # Mise à jour des informations de base
        parent.first_name = request.POST.get('first_name', '')
        parent.last_name = request.POST.get('last_name', '')
        parent.email = request.POST.get('email', '')
        
        # Mise à jour des informations du profil
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        
        if request.POST.get('date_of_birth'):
            profile.date_of_birth = request.POST.get('date_of_birth')
            
        # Informations personnelles supplémentaires
        profile.gender = request.POST.get('gender', '')
        profile.place_of_birth = request.POST.get('place_of_birth', '')
        profile.nationality = request.POST.get('nationality', '')
        profile.id_card_number = request.POST.get('id_card_number', '')
        profile.civil_status = request.POST.get('civil_status', '')
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        
        # Informations spécifiques aux parents
        if request.POST.get('number_of_children'):
            profile.number_of_children = int(request.POST.get('number_of_children'))
        profile.occupation = request.POST.get('occupation', '')
        profile.employer = request.POST.get('employer', '')
        profile.work_phone = request.POST.get('work_phone', '')
        
        # Sauvegarde
        parent.save()
        profile.save()
        
        # Gestion de la photo de profil
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
        
        messages.success(request, 'Parent mis à jour avec succès!')
        return redirect('auth_app:parent_list')
    
    context = {
        'parent': parent,
        'profile': profile,
        'title': 'Modifier un parent',
    }
    return render(request, 'auth_app/admin/parent_form.html', context)

@login_required
@user_passes_test(is_admin)
def parent_detail(request, pk):
    parent = get_object_or_404(User, pk=pk)
    # Récupérer les enfants associés à ce parent
    children_relationships = ParentStudentRelationship.objects.filter(parent=parent)
    
    return render(request, 'auth_app/admin/parent_detail.html', {
        'parent': parent,
        'profile': parent.userprofile,
        'children_relationships': children_relationships
    })

@login_required
@user_passes_test(is_admin)
def parent_delete(request, pk):
    parent = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        parent.delete()
        messages.success(request, 'Parent supprimé avec succès!')
        return redirect('auth_app:parent_list')
    return render(request, 'auth_app/admin/parent_confirm_delete.html', {'parent': parent})

# Vues pour la gestion des élèves
@login_required
@user_passes_test(is_admin)
def student_list(request):
    students = User.objects.filter(userprofile__user_type='student')
    return render(request, 'auth_app/admin/student_list.html', {'students': students})

@login_required
@user_passes_test(is_admin)
def student_create(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            student = form.save()
            
            # Gérer les relations avec les parents si spécifiées
            parent_ids = request.POST.getlist('parents')
            relationship_types = request.POST.getlist('relationship_types')
            primary_contact_id = request.POST.get('primary_contact')
            
            for i, parent_id in enumerate(parent_ids):
                if parent_id:  # S'assurer que l'ID n'est pas vide
                    parent = get_object_or_404(User, pk=parent_id)
                    relationship_type = relationship_types[i] if i < len(relationship_types) else 'guardian'
                    
                    # Créer la relation parent-élève
                    ParentStudentRelationship.objects.create(
                        parent=parent,
                        student=student,
                        relationship_type=relationship_type,
                        is_primary_contact=(parent_id == primary_contact_id)
                    )
            
            messages.success(request, 'Élève créé avec succès!')
            return redirect('auth_app:student_list')
        else:
            # Afficher les erreurs du formulaire pour le débogage
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Utiliser le formulaire spécifique pour les élèves
        form = StudentCreationForm()
        # Récupérer tous les parents pour le formulaire
        parents = User.objects.filter(userprofile__user_type='parent')
    
    return render(request, 'auth_app/admin/student_form.html', {
        'form': form, 
        'title': 'Créer un élève',
        'parents': parents,
        'parent_relationship_map': {}  # Vide pour la création
    })

@login_required
@user_passes_test(is_admin)
def student_edit(request, pk):
    student = get_object_or_404(User, pk=pk)
    profile = student.userprofile
    
    if request.method == 'POST':
        # Mise à jour des informations de base
        student.first_name = request.POST.get('first_name', '')
        student.last_name = request.POST.get('last_name', '')
        student.email = request.POST.get('email', '')
        
        # Mise à jour des informations du profil
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        
        if request.POST.get('date_of_birth'):
            profile.date_of_birth = request.POST.get('date_of_birth')
            
        # Informations personnelles supplémentaires
        profile.gender = request.POST.get('gender', '')
        profile.place_of_birth = request.POST.get('place_of_birth', '')
        profile.nationality = request.POST.get('nationality', '')
        profile.id_card_number = request.POST.get('id_card_number', '')
        profile.civil_status = request.POST.get('civil_status', '')
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        
        # Informations spécifiques aux élèves
        profile.student_id = request.POST.get('student_id', '')
        profile.blood_type = request.POST.get('blood_type', '')
        profile.allergies = request.POST.get('allergies', '')
        profile.medical_conditions = request.POST.get('medical_conditions', '')
        profile.previous_school = request.POST.get('previous_school', '')
        profile.previous_school_address = request.POST.get('previous_school_address', '')
        
        # Sauvegarde
        student.save()
        profile.save()
        
        # Mise à jour des relations avec les parents
        ParentStudentRelationship.objects.filter(student=student).delete()
        parent_ids = request.POST.getlist('parents')
        relationship_types = request.POST.getlist('relationship_types')
        primary_contact_id = request.POST.get('primary_contact')
        
        for i, parent_id in enumerate(parent_ids):
            if parent_id:  # S'assurer que l'ID n'est pas vide
                parent = get_object_or_404(User, pk=parent_id)
                relationship_type = relationship_types[i] if i < len(relationship_types) else 'guardian'
                
                # Créer la relation parent-élève
                ParentStudentRelationship.objects.create(
                    parent=parent,
                    student=student,
                    relationship_type=relationship_type,
                    is_primary_contact=(parent_id == primary_contact_id)
                )
        
        # Gestion de la photo de profil
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
        
        messages.success(request, 'Élève mis à jour avec succès!')
        return redirect('auth_app:student_list')
    
    # Récupérer les relations parent-élève existantes
    parent_relationships = ParentStudentRelationship.objects.filter(student=student)
    
    # Créer un dictionnaire pour mapper les IDs de parents à leurs relations
    parent_relationship_map = {}
    primary_contact_id = None
    
    for relationship in parent_relationships:
        parent_relationship_map[relationship.parent.pk] = relationship.relationship_type
        if relationship.is_primary_contact:
            primary_contact_id = relationship.parent.pk
    
    # Récupérer tous les parents pour le formulaire
    parents = User.objects.filter(userprofile__user_type='parent')
    
    context = {
        'student': student,
        'profile': profile,
        'title': 'Modifier un élève',
        'parents': parents,
        'parent_relationship_map': parent_relationship_map,
        'primary_contact_id': primary_contact_id
    }
    return render(request, 'auth_app/admin/student_form.html', context)

@login_required
@user_passes_test(is_admin)
def student_detail(request, pk):
    student = get_object_or_404(User, pk=pk)
    # Récupérer les parents associés à cet élève
    parent_relationships = ParentStudentRelationship.objects.filter(student=student)
    
    return render(request, 'auth_app/admin/student_detail.html', {
        'student': student,
        'profile': student.userprofile,
        'parent_relationships': parent_relationships
    })

@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    student = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Élève supprimé avec succès!')
        return redirect('auth_app:student_list')
    return render(request, 'auth_app/admin/student_confirm_delete.html', {'student': student})

# Dans auth_app/views.py
@login_required
@user_passes_test(is_admin)
def add_parent_to_student(request, student_pk):
    student = get_object_or_404(User, pk=student_pk)
    
    if request.method == 'POST':
        form = ParentStudentRelationshipForm(request.POST, student=student)
        if form.is_valid():
            relationship = form.save(commit=False)
            relationship.student = student
            relationship.save()
            messages.success(request, 'Parent associé avec succès!')
            return redirect('auth_app:student_detail', student_pk)
    else:
        form = ParentStudentRelationshipForm(student=student)
    
    return render(request, 'auth_app/admin/add_parent_to_student.html', {
        'form': form,
        'student': student,
        'title': f'Ajouter un parent à {student.get_full_name}'
    })

@login_required
@user_passes_test(is_admin)
def delete_parent_student_relationship(request, relationship_pk):
    relationship = get_object_or_404(ParentStudentRelationship, pk=relationship_pk)
    parent_pk = relationship.parent.pk
    
    if request.method == 'POST':
        relationship.delete()
        messages.success(request, 'Relation supprimée avec succès!')
        return redirect('auth_app:parent_detail', parent_pk)
    
    return render(request, 'auth_app/admin/confirm_delete_relationship.html', {
        'relationship': relationship
    })


