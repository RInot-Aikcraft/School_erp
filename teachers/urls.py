# teachers/urls.py
from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('classes/', views.teacher_classes_list, name='classes_list'),
    path('classes/<int:pk>/', views.teacher_class_detail, name='class_detail'),
    path('schedule/', views.teacher_schedule, name='schedule'),
]