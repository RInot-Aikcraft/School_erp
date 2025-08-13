from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('', views.redirect_to_login, name='redirect_to_login'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # URLs admin
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/update/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # URLs enseignant - MODIFIÉ pour rediriger vers le module teachers
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # URLs pour la gestion des enseignants (admin seulement)
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
    
    # URLs élève
    path('student/', views.student_dashboard, name='student_dashboard'),
    
    # URLs parent
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    # Ajoutez ces URLs à votre urlpatterns existant

    path('parents/', views.parent_list, name='parent_list'),
    path('parents/create/', views.parent_create, name='parent_create'),
    path('parents/<int:pk>/edit/', views.parent_edit, name='parent_edit'),
    path('parents/<int:pk>/', views.parent_detail, name='parent_detail'),
    path('parents/<int:pk>/delete/', views.parent_delete, name='parent_delete'),

    # Ajoutez ces URLs à votre urlpatterns existant
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    # Dans auth_app/urls.py
    path('students/<int:student_pk>/add-parent/', views.add_parent_to_student, name='add_parent_to_student'),
    path('parent-relationships/<int:relationship_pk>/delete/', views.delete_parent_student_relationship, name='delete_parent_student_relationship'),
]


