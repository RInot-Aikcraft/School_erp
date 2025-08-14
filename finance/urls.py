from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # URLs pour TypeFrais
    path('type-frais/', views.liste_type_frais, name='liste_type_frais'),
    path('type-frais/ajouter/', views.ajouter_type_frais, name='ajouter_type_frais'),
    path('type-frais/modifier/<int:pk>/', views.modifier_type_frais, name='modifier_type_frais'),
    path('type-frais/supprimer/<int:pk>/', views.supprimer_type_frais, name='supprimer_type_frais'),
    
    # URLs pour TypeCaisse
    path('type-caisse/', views.liste_type_caisse, name='liste_type_caisse'),
    path('type-caisse/ajouter/', views.ajouter_type_caisse, name='ajouter_type_caisse'),
    path('type-caisse/modifier/<int:pk>/', views.modifier_type_caisse, name='modifier_type_caisse'),
    path('type-caisse/supprimer/<int:pk>/', views.supprimer_type_caisse, name='supprimer_type_caisse'),
    
    # URLs pour Paiement
    path('paiements/', views.liste_paiements, name='liste_paiements'),
    path('paiements/ajouter/', views.ajouter_paiement, name='ajouter_paiement'),
    path('paiements/modifier/<int:pk>/', views.modifier_paiement, name='modifier_paiement'),
    path('paiements/supprimer/<int:pk>/', views.supprimer_paiement, name='supprimer_paiement'),
    path('paiements/detail/<int:pk>/', views.detail_paiement, name='detail_paiement'),
    path('paiements/valider/<int:pk>/', views.valider_paiement, name='valider_paiement'),
    path('paiements/annuler/<int:pk>/', views.annuler_paiement, name='annuler_paiement'),
    path('inscriptions/', views.liste_inscriptions, name='liste_inscriptions'),
    path('inscriptions/ajouter/', views.ajouter_inscription, name='ajouter_inscription'),
    path('inscriptions/modifier/<int:pk>/', views.modifier_inscription, name='modifier_inscription'),
    path('inscriptions/supprimer/<int:pk>/', views.supprimer_inscription, name='supprimer_inscription'),
    path('inscriptions/detail/<int:pk>/', views.detail_inscription, name='detail_inscription'),
    path('inscriptions/confirmer/<int:pk>/', views.confirmer_inscription, name='confirmer_inscription'),
    path('inscriptions/<int:pk>/ajouter-paiement/', views.ajouter_paiement_inscription, name='ajouter_paiement_inscription'),
     path('', views.liste, name='liste'),
    
    # URL AJAX pour récupérer les classes par année scolaire
    path('api/get-classes-by-year/', views.get_classes_by_year, name='get_classes_by_year'),
]
