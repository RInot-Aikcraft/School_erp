from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # URLs pour les types de frais
    path('fee-types/', views.fee_type_list, name='fee_type_list'),
    path('fee-types/create/', views.fee_type_create, name='fee_type_create'),
    
    # URLs pour les structures de frais
    path('fee-structures/', views.fee_structure_list, name='fee_structure_list'),
    path('fee-structures/create/', views.fee_structure_create, name='fee_structure_create'),
    
    # URLs pour les frais des élèves
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/student/<int:student_id>/', views.student_fee_list, name='student_fee_list'),
    
    # URLs pour les paiements
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/<int:fee_id>/', views.payment_create, name='payment_create'),
    
    # URL pour générer les frais pour une classe
    path('generate-fees/<int:class_id>/', views.generate_fees_for_class, name='generate_fees_for_class'),  
]