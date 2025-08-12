from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('', views.redirect_to_login, name='redirect_to_login'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # URLs admin - utilisez un préfixe différent pour éviter les conflits
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/update/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # URLs enseignant
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    # URLs pour la gestion des enseignants
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
    
    # URLs élève
    path('student/', views.student_dashboard, name='student_dashboard'),
    
    # URLs parent
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
]