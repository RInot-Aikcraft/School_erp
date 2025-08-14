from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),
    path('classes/<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),
    path('classes/<int:class_pk>/add-subject/', views.add_subject_to_class, name='add_subject_to_class'),
    
    path('class-subjects/<int:class_subject_pk>/delete/', views.remove_subject_from_class, name='remove_subject_from_class'),
    path('api/get-teachers-for-subject/', views.get_teachers_for_subject, name='get_teachers_for_subject'),

    path('classes/<int:class_pk>/schedule/', views.class_schedule, name='class_schedule'),
    path('schedules/<int:schedule_pk>/add-entry/', views.add_schedule_entry, name='add_schedule_entry'),


    
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/create/', views.grade_create, name='grade_create'),
    path('grades/<int:pk>/', views.grade_detail, name='grade_detail'),
    path('grades/<int:pk>/edit/', views.grade_edit, name='grade_edit'),
    path('grades/<int:pk>/delete/', views.grade_delete, name='grade_delete'),

  
    path('levels/', views.class_level_list, name='class_level_list'),
    path('levels/create/', views.class_level_create, name='class_level_create'),
    path('levels/<int:pk>/', views.class_level_detail, name='class_level_detail'),
    path('levels/<int:pk>/edit/', views.class_level_edit, name='class_level_edit'),
    path('levels/<int:pk>/delete/', views.class_level_delete, name='class_level_delete'),



]