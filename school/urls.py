from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    path('detail/', views.school_detail, name='school_detail'),
    path('edit/', views.school_edit, name='school_edit'),
    
    path('years/', views.school_year_list, name='school_year_list'),
    path('years/create/', views.school_year_create, name='school_year_create'),
    path('years/<int:pk>/', views.school_year_detail, name='school_year_detail'),
    path('years/<int:pk>/edit/', views.school_year_edit, name='school_year_edit'),
    path('years/<int:pk>/delete/', views.school_year_delete, name='school_year_delete'),
    
    path('periods/', views.period_list, name='period_list'),
    path('periods/create/', views.period_create, name='period_create'),
    path('periods/<int:pk>/edit/', views.period_edit, name='period_edit'),
    path('periods/<int:pk>/delete/', views.period_delete, name='period_delete'),
    
    path('holidays/', views.holiday_list, name='holiday_list'),
    path('holidays/create/', views.holiday_create, name='holiday_create'),
    path('holidays/<int:pk>/edit/', views.holiday_edit, name='holiday_edit'),
    path('holidays/<int:pk>/delete/', views.holiday_delete, name='holiday_delete'),
]