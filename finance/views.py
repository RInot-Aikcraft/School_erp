from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Paiement, TypeFrais, TypeCaisse
from academics.models import Class, ClassLevel
from school.models import SchoolYear
from django.contrib.auth.models import User


@login_required
def liste_type_frais(request):
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active
    try:
        active_school_year = SchoolYear.objects.get(current=True)  # Utilisation de 'current' au lieu de 'is_active'
    except SchoolYear.DoesNotExist:
        active_school_year = None
    
    # Récupérer l'année sélectionnée (par défaut l'année active)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        try:
            selected_year = SchoolYear.objects.get(pk=selected_year_id)
        except SchoolYear.DoesNotExist:
            selected_year = active_school_year
    else:
        selected_year = active_school_year
    
    # Filtrer les types de frais par année scolaire si une année est sélectionnée
    if selected_year:
        type_frais_list = TypeFrais.objects.filter(annee_scolaire=selected_year)
    else:
        type_frais_list = TypeFrais.objects.all()
    
    context = {
        'type_frais_list': type_frais_list,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
    }
    return render(request, 'finance/type_frais/liste.html', context)

@login_required
def ajouter_type_frais(request):
    if request.method == 'POST':
        nom_frais = request.POST.get('nom_frais')
        classe_id = request.POST.get('classe')
        annee_scolaire_id = request.POST.get('annee_scolaire')
        montant = request.POST.get('montant')
        periodicite = request.POST.get('periodicite')
        frais_inscription = request.POST.get('frais_inscription') == 'on'  # Récupération de la valeur du checkbox
        
        try:
            classe = Class.objects.get(id=classe_id)
            annee_scolaire = SchoolYear.objects.get(id=annee_scolaire_id)
            
            type_frais = TypeFrais(
                nom_frais=nom_frais,
                classe=classe,
                annee_scolaire=annee_scolaire,
                montant=montant,
                periodicite=periodicite,
                frais_inscription=frais_inscription  # Ajout du champ
            )
            type_frais.save()
            messages.success(request, "Le type de frais a été ajouté avec succès.")
            return redirect('finance:liste_type_frais')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    classes = Class.objects.all()
    annees_scolaires = SchoolYear.objects.all()
    context = {
        'classes': classes,
        'annees_scolaires': annees_scolaires,
        'periodicite_choices': TypeFrais.PERIODICITE_CHOICES,
    }
    return render(request, 'finance/type_frais/ajouter.html', context)

@login_required
def modifier_type_frais(request, pk):
    type_frais = get_object_or_404(TypeFrais, pk=pk)
    
    if request.method == 'POST':
        type_frais.nom_frais = request.POST.get('nom_frais')
        type_frais.classe_id = request.POST.get('classe')
        type_frais.annee_scolaire_id = request.POST.get('annee_scolaire')
        type_frais.montant = request.POST.get('montant')
        type_frais.periodicite = request.POST.get('periodicite')
        type_frais.frais_inscription = request.POST.get('frais_inscription') == 'on'  # Ajout du champ
        
        try:
            type_frais.save()
            messages.success(request, "Le type de frais a été modifié avec succès.")
            return redirect('finance:liste_type_frais')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    classes = Class.objects.all()
    annees_scolaires = SchoolYear.objects.all()
    context = {
        'type_frais': type_frais,
        'classes': classes,
        'annees_scolaires': annees_scolaires,
        'periodicite_choices': TypeFrais.PERIODICITE_CHOICES,
    }
    return render(request, 'finance/type_frais/modifier.html', context)

@login_required
def supprimer_type_frais(request, pk):
    type_frais = get_object_or_404(TypeFrais, pk=pk)
    
    if request.method == 'POST':
        try:
            type_frais.delete()
            messages.success(request, "Le type de frais a été supprimé avec succès.")
            return redirect('finance:liste_type_frais')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    return render(request, 'finance/type_frais/supprimer.html', {'type_frais': type_frais})



@login_required
def liste_type_caisse(request):
    type_caisse_list = TypeCaisse.objects.all()
    context = {
        'type_caisse_list': type_caisse_list,
    }
    return render(request, 'finance/type_caisse/liste.html', context)

@login_required
def ajouter_type_caisse(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        code = request.POST.get('code')
        description = request.POST.get('description')
        est_active = request.POST.get('est_active') == 'on'
        couleur = request.POST.get('couleur', '#3498db')
        
        try:
            type_caisse = TypeCaisse(
                nom=nom,
                code=code,
                description=description,
                est_active=est_active,
                couleur=couleur
            )
            type_caisse.save()
            messages.success(request, "Le type de caisse a été ajouté avec succès.")
            return redirect('finance:liste_type_caisse')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    context = {
        'couleur_defaut': '#3498db',
    }
    return render(request, 'finance/type_caisse/ajouter.html', context)

@login_required
def modifier_type_caisse(request, pk):
    type_caisse = get_object_or_404(TypeCaisse, pk=pk)
    
    if request.method == 'POST':
        type_caisse.nom = request.POST.get('nom')
        type_caisse.code = request.POST.get('code')
        type_caisse.description = request.POST.get('description')
        type_caisse.est_active = request.POST.get('est_active') == 'on'
        type_caisse.couleur = request.POST.get('couleur', '#3498db')
        
        try:
            type_caisse.save()
            messages.success(request, "Le type de caisse a été modifié avec succès.")
            return redirect('finance:liste_type_caisse')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    context = {
        'type_caisse': type_caisse,
    }
    return render(request, 'finance/type_caisse/modifier.html', context)

@login_required
def supprimer_type_caisse(request, pk):
    type_caisse = get_object_or_404(TypeCaisse, pk=pk)
    
    if request.method == 'POST':
        try:
            type_caisse.delete()
            messages.success(request, "Le type de caisse a été supprimé avec succès.")
            return redirect('finance:liste_type_caisse')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    return render(request, 'finance/type_caisse/supprimer.html', {'type_caisse': type_caisse})


@login_required
def liste_paiements(request):
    # Récupérer les paramètres de filtrage
    eleve_id = request.GET.get('eleve')
    type_frais_id = request.GET.get('type_frais')
    type_caisse_id = request.GET.get('type_caisse')
    statut = request.GET.get('statut')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active
    try:
        active_school_year = SchoolYear.objects.get(current=True)
    except SchoolYear.DoesNotExist:
        active_school_year = None
    
    # Récupérer l'année sélectionnée (par défaut l'année active)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        try:
            selected_year = SchoolYear.objects.get(pk=selected_year_id)
        except SchoolYear.DoesNotExist:
            selected_year = active_school_year
    else:
        selected_year = active_school_year
    
    # Filtrer les paiements
    paiements = Paiement.objects.all()
    
    # Filtrer par année scolaire
    if selected_year:
        paiements = paiements.filter(type_frais__annee_scolaire=selected_year)
    
    # Appliquer les autres filtres
    if eleve_id:
        paiements = paiements.filter(eleve_id=eleve_id)
    if type_frais_id:
        paiements = paiements.filter(type_frais_id=type_frais_id)
    if type_caisse_id:
        paiements = paiements.filter(type_caisse_id=type_caisse_id)
    if statut:
        paiements = paiements.filter(statut=statut)
    if date_debut:
        paiements = paiements.filter(date_paiement__gte=date_debut)
    if date_fin:
        paiements = paiements.filter(date_paiement__lte=date_fin)
    
    # Récupérer les données pour les filtres
    eleves = User.objects.filter(userprofile__user_type='student')
    types_frais = TypeFrais.objects.all()
    types_caisse = TypeCaisse.objects.filter(est_active=True)
    
    # Calculer les statistiques
    from django.db.models import Sum, Count
    total_montant = paiements.aggregate(total=Sum('montant'))['total'] or 0
    count_en_attente = paiements.filter(statut='EN_ATTENTE').count()
    count_valide = paiements.filter(statut='VALIDE').count()
    
    context = {
        'paiements': paiements,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
        'eleves': eleves,
        'types_frais': types_frais,
        'types_caisse': types_caisse,
        'statut_choices': Paiement.STATUT_CHOICES,
        'mode_paiement_choices': Paiement.MODE_PAIEMENT_CHOICES,
        # Conserver les valeurs des filtres pour réaffichage
        'filtre_eleve': eleve_id,
        'filtre_type_frais': type_frais_id,
        'filtre_type_caisse': type_caisse_id,
        'filtre_statut': statut,
        'filtre_date_debut': date_debut,
        'filtre_date_fin': date_fin,
        # Ajouter les statistiques
        'total_montant': total_montant,
        'count_en_attente': count_en_attente,
        'count_valide': count_valide,
    }
    return render(request, 'finance/paiements/liste.html', context)

@login_required
def ajouter_paiement(request):
    # Récupérer les paramètres de l'URL
    eleve_id = request.GET.get('eleve_id')
    mois = request.GET.get('mois')
    montant = request.GET.get('montant')
    inscription_id = request.GET.get('inscription_id')
    type_paiement = request.GET.get('type_paiement')  # Nouveau paramètre pour distinguer les types de paiement
    
    # Récupérer l'inscription si un ID est fourni
    inscription = None
    if inscription_id:
        try:
            inscription = Inscription.objects.get(pk=inscription_id)
        except Inscription.DoesNotExist:
            pass
    
    # Récupérer l'élève si un ID est fourni
    eleve = None
    if eleve_id:
        try:
            eleve = User.objects.get(pk=eleve_id)
        except User.DoesNotExist:
            pass
    
    # Récupérer le nom du mois si un mois est fourni
    mois_nom = None
    if mois:
        mois_nom = dict(Paiement.MOIS_CHOICES).get(int(mois), None)
    
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve')
        type_frais_id = request.POST.get('type_frais')
        type_caisse_id = request.POST.get('type_caisse')
        montant = request.POST.get('montant')
        mois = request.POST.get('mois')
        date_paiement = request.POST.get('date_paiement')
        mode_paiement = request.POST.get('mode_paiement')
        reference = request.POST.get('reference')
        notes = request.POST.get('notes')
        
        try:
            eleve = User.objects.get(id=eleve_id)
            type_frais = TypeFrais.objects.get(id=type_frais_id)
            type_caisse = TypeCaisse.objects.get(id=type_caisse_id)
            
            paiement = Paiement(
                eleve=eleve,
                type_frais=type_frais,
                type_caisse=type_caisse,
                montant=montant,
                mois=mois if mois else None,
                date_paiement=date_paiement,
                mode_paiement=mode_paiement,
                reference=reference,
                notes=notes,
                enregistre_par=request.user,
                statut='VALIDE'  # Par défaut, on considère le paiement comme validé
            )
            paiement.save()
            messages.success(request, "Le paiement a été enregistré avec succès.")
            
            # Rediriger vers la page appropriée
            if inscription:
                return redirect('finance:detail_inscription', pk=inscription.pk)
            else:
                return redirect('finance:liste_paiements')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    # Récupérer les données pour les formulaires
    eleves = User.objects.filter(userprofile__user_type='student')
    types_frais = TypeFrais.objects.all()
    types_caisse = TypeCaisse.objects.filter(est_active=True)
    
    # Si une inscription est fournie, filtrer les types de frais pour cette classe
    if inscription:
        # Si c'est un paiement d'écolage (mois fourni)
        if mois:
            types_frais = TypeFrais.objects.filter(
                classe=inscription.classe_demandee,
                annee_scolaire=inscription.annee_scolaire,
                frais_inscription=False,  # Exclure les frais d'inscription
                periodicite='MENSUEL'  # Ne prendre que les frais mensuels
            )
        # Sinon, si c'est explicitement un paiement d'inscription
        elif type_paiement == 'inscription':
            types_frais = TypeFrais.objects.filter(
                classe=inscription.classe_demandee,
                annee_scolaire=inscription.annee_scolaire,
                frais_inscription=True  # Ne prendre que les frais d'inscription
            )
        # Sinon, afficher tous les types de frais pour cette classe
        else:
            types_frais = TypeFrais.objects.filter(
                classe=inscription.classe_demandee,
                annee_scolaire=inscription.annee_scolaire
            )
    
    context = {
        'eleves': eleves,
        'types_frais': types_frais,
        'types_caisse': types_caisse,
        'statut_choices': Paiement.STATUT_CHOICES,
        'mode_paiement_choices': Paiement.MODE_PAIEMENT_CHOICES,
        'mois_choices': Paiement.MOIS_CHOICES,
        'inscription': inscription,
        'eleve': eleve,
        'mois': mois,
        'mois_nom': mois_nom,
        'montant': montant,
    }
    
    # Déterminer quel template utiliser
    if mois and eleve and inscription:
        return render(request, 'finance/paiements/ajouter_ecolage.html', context)
    else:
        return render(request, 'finance/paiements/ajouter.html', context)


@login_required
def modifier_paiement(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    
    if request.method == 'POST':
        paiement.eleve_id = request.POST.get('eleve')
        paiement.type_frais_id = request.POST.get('type_frais')
        paiement.type_caisse_id = request.POST.get('type_caisse')
        paiement.montant = request.POST.get('montant')
        paiement.mois = request.POST.get('mois') if request.POST.get('mois') else None
        paiement.date_paiement = request.POST.get('date_paiement')
        paiement.statut = request.POST.get('statut')
        paiement.mode_paiement = request.POST.get('mode_paiement')
        paiement.reference = request.POST.get('reference')
        paiement.notes = request.POST.get('notes')
        
        try:
            paiement.save()
            messages.success(request, "Le paiement a été modifié avec succès.")
            return redirect('finance:liste_paiements')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    # Récupérer les données pour les formulaires
    eleves = User.objects.filter(userprofile__user_type='student')
    types_frais = TypeFrais.objects.all()
    types_caisse = TypeCaisse.objects.filter(est_active=True)
    
    context = {
        'paiement': paiement,
        'eleves': eleves,
        'types_frais': types_frais,
        'types_caisse': types_caisse,
        'statut_choices': Paiement.STATUT_CHOICES,
        'mode_paiement_choices': Paiement.MODE_PAIEMENT_CHOICES,
        'mois_choices': Paiement.MOIS_CHOICES,
    }
    return render(request, 'finance/paiements/modifier.html', context)
@login_required
def supprimer_paiement(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    
    if request.method == 'POST':
        try:
            paiement.delete()
            messages.success(request, "Le paiement a été supprimé avec succès.")
            return redirect('finance:liste_paiements')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    return render(request, 'finance/paiements/supprimer.html', {'paiement': paiement})

@login_required
def detail_paiement(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    
    context = {
        'paiement': paiement,
    }
    return render(request, 'finance/paiements/detail.html', context)

@login_required
def valider_paiement(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    
    if request.method == 'POST':
        try:
            paiement.statut = 'VALIDE'
            paiement.save()
            messages.success(request, "Le paiement a été validé avec succès.")
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
        
        return redirect('finance:detail_paiement', pk=pk)
    
    return render(request, 'finance/paiements/valider.html', {'paiement': paiement})

@login_required
def annuler_paiement(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    
    if request.method == 'POST':
        try:
            paiement.statut = 'ANNULE'
            paiement.save()
            messages.success(request, "Le paiement a été annulé avec succès.")
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
        
        return redirect('finance:detail_paiement', pk=pk)
    
    return render(request, 'finance/paiements/annuler.html', {'paiement': paiement})


# Ajoutez ces vues à la suite de vos vues existantes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Inscription, TypeFrais, TypeCaisse, Paiement
from academics.models import Class, Enrollment
from school.models import SchoolYear

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def liste_inscriptions(request):
    # Récupérer les paramètres de filtrage
    statut = request.GET.get('statut')
    annee_scolaire_id = request.GET.get('annee_scolaire')
    classe_id = request.GET.get('classe')
    
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active
    try:
        active_school_year = SchoolYear.objects.get(current=True)
    except SchoolYear.DoesNotExist:
        active_school_year = None
    
    # Récupérer l'année sélectionnée (par défaut l'année active)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        try:
            selected_year = SchoolYear.objects.get(pk=selected_year_id)
        except SchoolYear.DoesNotExist:
            selected_year = active_school_year
    else:
        selected_year = active_school_year
    
    # Filtrer les inscriptions
    inscriptions = Inscription.objects.all()
    
    # Filtrer par année scolaire
    if selected_year:
        inscriptions = inscriptions.filter(annee_scolaire=selected_year)
    
    # Appliquer les autres filtres
    if statut:
        inscriptions = inscriptions.filter(statut=statut)
    if classe_id:
        inscriptions = inscriptions.filter(classe_demandee_id=classe_id)
    
    # Récupérer les données pour les filtres
    classes = Class.objects.filter(school_year=selected_year) if selected_year else Class.objects.none()
    
    # Calculer les statistiques de base
    total_inscriptions = inscriptions.count()
    total_en_attente = inscriptions.filter(statut='EN_ATTENTE').count()
    total_acceptees = inscriptions.filter(statut='ACCEPTÉE').count()
    total_confirmees = inscriptions.filter(statut='CONFIRMÉE').count()
    
    # Calculer les statistiques financières
    total_ecolages_impayes = 0
    total_frais_inscription_impayes = 0
    
    # Pour chaque inscription, calculer les écolages impayés
    for inscription in inscriptions:
        # Récupérer les écolages impayés pour cette inscription
        ecolages_impayes = inscription.get_ecolages_impayes()
        # Compter les écolages impayés (statut temporel "passé" ou "en_cours" et non payés)
        for mois in ecolages_impayes:
            if mois['statut_temporel'] in ['passé', 'en_cours'] and not mois['est_paye']:
                total_ecolages_impayes += 1
        
        # Vérifier si les frais d'inscription sont impayés
        if inscription.get_solde() > 0:
            total_frais_inscription_impayes += 1
    
    context = {
        'inscriptions': inscriptions,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
        'classes': classes,
        'statut_choices': Inscription.STATUT_CHOICES,
        # Conserver les valeurs des filtres pour réaffichage
        'filtre_statut': statut,
        'filtre_classe': classe_id,
        # Ajouter les statistiques
        'total_inscriptions': total_inscriptions,
        'total_en_attente': total_en_attente,
        'total_acceptees': total_acceptees,
        'total_confirmees': total_confirmees,
        # Ajouter les statistiques financières
        'total_ecolages_impayes': total_ecolages_impayes,
        'total_frais_inscription_impayes': total_frais_inscription_impayes,
    }
    return render(request, 'finance/inscriptions/liste.html', context)

@login_required
@user_passes_test(is_admin)
def detail_inscription(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    
    # Récupérer uniquement les types de frais d'inscription associés à cette inscription
    types_frais = inscription.get_types_frais()
    
    # Récupérer uniquement les paiements associés aux frais d'inscription
    paiements_inscription = inscription.get_paiements()
    
    # Récupérer la liste de tous les mois avec leur statut de paiement
    tous_les_mois = inscription.get_ecolages_impayes()
    
    # Filtrer pour ne compter que les mois passés ou en cours pour les totaux
    mois_relevant = [mois for mois in tous_les_mois if mois['statut_temporel'] in ['passé', 'en_cours']]
    
    # Calculer les totaux pour l'écolage (uniquement pour les mois passés ou en cours)
    total_ecolage_du = sum(mois['montant_du'] for mois in mois_relevant)
    total_ecolage_paye = sum(mois['montant_paye'] for mois in mois_relevant)
    solde_ecolage = total_ecolage_du - total_ecolage_paye
    
    # Calculer le nombre de mois payés et impayés (uniquement pour les mois passés ou en cours)
    mois_payes_count = sum(1 for mois in mois_relevant if mois['est_paye'])
    mois_impayes_count = sum(1 for mois in mois_relevant if not mois['est_paye'])
    
    # Calculer le nombre de mois à venir
    mois_avenir_count = sum(1 for mois in tous_les_mois if mois['statut_temporel'] == 'à_venir')
    
    # Récupérer les autres paiements (ni inscription, ni écolage mensuel)
    types_frais_ecolage = TypeFrais.objects.filter(
        classe=inscription.classe_demandee,
        annee_scolaire=inscription.annee_scolaire,
        periodicite__in=['MENSUEL', 'TRIMESTRIEL', 'ANNUEL'],
        frais_inscription=False
    )
    
    autres_paiements = Paiement.objects.filter(
        eleve=inscription.eleve
    ).exclude(
        type_frais__in=types_frais
    )
    
    # Calculer les montants pour les frais d'inscription
    frais_total_inscription = inscription.calculer_frais_inscription()
    montant_paye_inscription = inscription.get_montant_paye()
    solde_inscription = inscription.get_solde()
    
    # Calculer les montants pour les autres frais
    total_autres_frais = sum(paiement.type_frais.montant for paiement in autres_paiements)
    montant_paye_autres = sum(paiement.montant for paiement in autres_paiements if paiement.statut == 'VALIDE')
    solde_autres = total_autres_frais - montant_paye_autres
    
    # Récupérer les types de caisse pour le formulaire de paiement
    types_caisse = TypeCaisse.objects.filter(est_active=True)
    
    context = {
        'inscription': inscription,
        'types_frais': types_frais,
        'paiements_inscription': paiements_inscription,
        'tous_les_mois': tous_les_mois,
        'total_ecolage_du': total_ecolage_du,
        'total_ecolage_paye': total_ecolage_paye,
        'solde_ecolage': solde_ecolage,
        'mois_payes_count': mois_payes_count,
        'mois_impayes_count': mois_impayes_count,
        'mois_avenir_count': mois_avenir_count,
        'frais_total_inscription': frais_total_inscription,
        'montant_paye_inscription': montant_paye_inscription,
        'solde_inscription': solde_inscription,
        'total_autres_frais': total_autres_frais,
        'montant_paye_autres': montant_paye_autres,
        'solde_autres': solde_autres,
        'types_caisse': types_caisse,
        'mode_paiement_choices': Paiement.MODE_PAIEMENT_CHOICES,
        'mois_choices': Paiement.MOIS_CHOICES,
    }
    return render(request, 'finance/inscriptions/detail.html', context)


@login_required
@user_passes_test(is_admin)
def ajouter_inscription(request):
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve')
        annee_scolaire_id = request.POST.get('annee_scolaire')
        classe_demandee_id = request.POST.get('classe_demandee')
        type_inscription = request.POST.get('type_inscription', 'PASSANT')
        notes = request.POST.get('notes')
        
        try:
            eleve = User.objects.get(id=eleve_id)
            annee_scolaire = SchoolYear.objects.get(id=annee_scolaire_id)
            classe_demandee = Class.objects.get(id=classe_demandee_id)
            
            # Vérifier si l'élève n'a pas déjà une inscription pour cette année scolaire
            if Inscription.objects.filter(eleve=eleve, annee_scolaire=annee_scolaire).exists():
                messages.error(request, "Cet élève a déjà une inscription pour cette année scolaire.")
                return redirect('finance:ajouter_inscription')
            
            inscription = Inscription(
                eleve=eleve,
                annee_scolaire=annee_scolaire,
                classe_demandee=classe_demandee,
                type_inscription=type_inscription,
                notes=notes
            )
            inscription.save()
            messages.success(request, "L'inscription a été créée avec succès.")
            return redirect('finance:detail_inscription', pk=inscription.pk)
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    # Récupérer les données pour les formulaires
    from auth_app.models import UserProfile
    eleves = User.objects.filter(userprofile__user_type='student')
    school_years = SchoolYear.objects.all()
    
    # Récupérer l'année scolaire active par défaut
    try:
        active_school_year = SchoolYear.objects.get(current=True)
    except SchoolYear.DoesNotExist:
        active_school_year = None
    
    context = {
        'eleves': eleves,
        'school_years': school_years,
        'active_school_year': active_school_year,
        'type_inscription_choices': Inscription.TYPE_INSCRIPTION_CHOICES,
    }
    return render(request, 'finance/inscriptions/ajouter.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_inscription(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    
    if request.method == 'POST':
        # On ne permet pas de modifier l'élève, l'année scolaire ou la classe demandée
        # car cela affecterait les paiements déjà enregistrés
        inscription.statut = request.POST.get('statut')
        inscription.classe_attribuee_id = request.POST.get('classe_attribuee')
        inscription.notes = request.POST.get('notes')
        
        # Si le statut est confirmé, définir la date de confirmation
        if inscription.statut == 'CONFIRMÉE' and not inscription.date_confirmation:
            inscription.date_confirmation = timezone.now()
        elif inscription.statut != 'CONFIRMÉE':
            inscription.date_confirmation = None
        
        try:
            inscription.save()
            messages.success(request, "L'inscription a été modifiée avec succès.")
            return redirect('finance:detail_inscription', pk=inscription.pk)
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    # Récupérer les classes de la même année scolaire pour l'assignation
    classes = Class.objects.filter(
        school_year=inscription.annee_scolaire,
        level=inscription.classe_demandee.level
    )
    
    context = {
        'inscription': inscription,
        'classes': classes,
        'statut_choices': Inscription.STATUT_CHOICES,
    }
    return render(request, 'finance/inscriptions/modifier.html', context)

@login_required
@user_passes_test(is_admin)
def supprimer_inscription(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    
    if request.method == 'POST':
        try:
            # Vérifier s'il y a des paiements associés
            if inscription.get_paiements().exists():
                messages.error(request, "Impossible de supprimer cette inscription car elle a des paiements associés.")
                return redirect('finance:detail_inscription', pk=inscription.pk)
            
            inscription.delete()
            messages.success(request, "L'inscription a été supprimée avec succès.")
            return redirect('finance:liste_inscriptions')
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    return render(request, 'finance/inscriptions/supprimer.html', {'inscription': inscription})

@login_required
@user_passes_test(is_admin)
def confirmer_inscription(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    
    if request.method == 'POST':
        success, message = inscription.confirmer_inscription()
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect('finance:detail_inscription', pk=inscription.pk)
    
    return render(request, 'finance/inscriptions/confirmer.html', {'inscription': inscription})

@login_required
@user_passes_test(is_admin)
def ajouter_paiement_inscription(request, pk):
    inscription = get_object_or_404(Inscription, pk=pk)
    
    if request.method == 'POST':
        type_frais_id = request.POST.get('type_frais')
        type_caisse_id = request.POST.get('type_caisse')
        montant = request.POST.get('montant')
        date_paiement = request.POST.get('date_paiement')
        mode_paiement = request.POST.get('mode_paiement')
        reference = request.POST.get('reference')
        notes = request.POST.get('notes')
        
        try:
            type_frais = TypeFrais.objects.get(id=type_frais_id)
            type_caisse = TypeCaisse.objects.get(id=type_caisse_id)
            
            # Vérifier que le type de frais est bien un frais d'inscription
            if not type_frais.frais_inscription:
                messages.error(request, "Ce type de frais n'est pas un frais d'inscription.")
                return redirect('finance:ajouter_paiement_inscription', pk=pk)
                
            # Vérifier que le type de frais est bien associé à la classe de l'inscription
            if type_frais.classe != inscription.classe_demandee or type_frais.annee_scolaire != inscription.annee_scolaire:
                messages.error(request, "Ce type de frais n'est pas associé à cette inscription.")
                return redirect('finance:ajouter_paiement_inscription', pk=pk)
            
            paiement = Paiement(
                eleve=inscription.eleve,
                type_frais=type_frais,
                type_caisse=type_caisse,
                montant=montant,
                date_paiement=date_paiement,
                mode_paiement=mode_paiement,
                reference=reference,
                notes=notes,
                enregistre_par=request.user,
                statut='VALIDE'
            )
            paiement.save()
            messages.success(request, "Le paiement a été enregistré avec succès.")
            return redirect('finance:detail_inscription', pk=inscription.pk)
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
    # Récupérer uniquement les types de frais d'inscription associés à cette inscription
    types_frais = inscription.get_types_frais()
    
    # Récupérer les types de caisse pour le formulaire
    types_caisse = TypeCaisse.objects.filter(est_active=True)
    
    context = {
        'inscription': inscription,
        'types_frais': types_frais,
        'types_caisse': types_caisse,
        'mode_paiement_choices': Paiement.MODE_PAIEMENT_CHOICES,
    }
    return render(request, 'finance/inscriptions/ajouter_paiement.html', context)

@login_required
@user_passes_test(is_admin)
def get_classes_by_year(request):
    """Vue AJAX pour récupérer les classes en fonction de l'année scolaire"""
    annee_scolaire_id = request.GET.get('annee_scolaire_id')
    
    if annee_scolaire_id:
        classes = Class.objects.filter(school_year_id=annee_scolaire_id)
        classes_data = []
        
        for classe in classes:
            # Calculer le nombre d'inscriptions confirmées pour cette classe
            inscriptions_count = Inscription.objects.filter(
                classe_demandee=classe,
                annee_scolaire_id=annee_scolaire_id,
                statut='CONFIRMÉE'
            ).count()
            
            places_disponibles = classe.max_students - inscriptions_count
            
            classes_data.append({
                'id': classe.id,
                'name': classe.name,
                'max_students': classe.max_students,
                'inscriptions_count': inscriptions_count,
                'places_disponibles': places_disponibles
            })
        
        return JsonResponse({'classes': classes_data})
    
    return JsonResponse({'classes': []})


@login_required
def liste(request):
    # Récupérer les paramètres de filtrage
    statut = request.GET.get('statut')
    annee_scolaire_id = request.GET.get('annee_scolaire')
    classe_id = request.GET.get('classe')
    
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active
    try:
        active_school_year = SchoolYear.objects.get(current=True)
    except SchoolYear.DoesNotExist:
        active_school_year = None
    
    # Récupérer l'année sélectionnée (par défaut l'année active)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        try:
            selected_year = SchoolYear.objects.get(pk=selected_year_id)
        except SchoolYear.DoesNotExist:
            selected_year = active_school_year
    else:
        selected_year = active_school_year
    
    # Filtrer les inscriptions
    inscriptions = Inscription.objects.all()
    
    # Filtrer par année scolaire
    if selected_year:
        inscriptions = inscriptions.filter(annee_scolaire=selected_year)
    
    # Appliquer les autres filtres
    if statut:
        inscriptions = inscriptions.filter(statut=statut)
    if classe_id:
        inscriptions = inscriptions.filter(classe_demandee_id=classe_id)
    
    # Récupérer les données pour les filtres
    classes = Class.objects.filter(school_year=selected_year) if selected_year else Class.objects.none()
    
    context = {
        'inscriptions': inscriptions,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
        'classes': classes,
        'statut_choices': Inscription.STATUT_CHOICES,
        # Conserver les valeurs des filtres pour réaffichage
        'filtre_statut': statut,
        'filtre_classe': classe_id,
    }
    return render(request, 'liste.html', context)


@login_required
@user_passes_test(is_admin)
def liste_ecolages_impayes(request):
    # Récupérer les paramètres de filtrage
    annee_scolaire_id = request.GET.get('school_year')
    classe_id = request.GET.get('classe')
    mois_id = request.GET.get('mois')
    
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active
    try:
        active_school_year = SchoolYear.objects.get(current=True)
    except SchoolYear.DoesNotExist:
        active_school_year = None
    
    # Récupérer l'année sélectionnée (par défaut l'année active)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        try:
            selected_year = SchoolYear.objects.get(pk=selected_year_id)
        except SchoolYear.DoesNotExist:
            selected_year = active_school_year
    else:
        selected_year = active_school_year
    
    # Récupérer toutes les classes de l'année scolaire sélectionnée
    classes = Class.objects.filter(school_year=selected_year) if selected_year else Class.objects.none()
    
    # Récupérer toutes les inscriptions de l'année scolaire sélectionnée
    inscriptions = Inscription.objects.filter(annee_scolaire=selected_year) if selected_year else Inscription.objects.none()
    
    # Appliquer le filtre de classe si spécifié
    if classe_id:
        inscriptions = inscriptions.filter(classe_demandee_id=classe_id)
    
    # Liste pour stocker les résultats
    resultats = []
    
    # Pour chaque inscription, récupérer les mois d'écolage impayés
    for inscription in inscriptions:
        ecolages_impayes = inscription.get_ecolages_impayes()
        
        # Filtrer pour ne garder que les mois impayés qui sont dans le passé ou en cours
        mois_impayes = [
            mois for mois in ecolages_impayes 
            if mois['statut_temporel'] in ['passé', 'en_cours'] and not mois['est_paye']
        ]
        
        # Filtrer par mois si spécifié
        if mois_id:
            mois_impayes = [mois for mois in mois_impayes if str(mois['mois']) == mois_id]
        
        # S'il y a des mois impayés, ajouter l'inscription aux résultats
        if mois_impayes:
            resultats.append({
                'inscription': inscription,
                'mois_impayes': mois_impayes,
                'total_mois_impayes': len(mois_impayes)
            })
    
    # Calculer le nombre total d'écolages impayés
    total_ecolages_impayes = sum(resultat['total_mois_impayes'] for resultat in resultats)
    
    # Obtenir la date actuelle pour déterminer les mois passés et en cours
    from datetime import date
    aujourd_hui = date.today()
    
    # Créer une liste des mois passés et en cours pour le filtre
    mois_disponibles = []
    if selected_year:
        current_date = selected_year.start_date
        while current_date <= selected_year.end_date:
            # Ne considérer que les mois passés ou en cours
            if (current_date.year < aujourd_hui.year or 
                (current_date.year == aujourd_hui.year and current_date.month <= aujourd_hui.month)):
                mois_disponibles.append({
                    'code': current_date.month,
                    'nom': dict(Paiement.MOIS_CHOICES).get(current_date.month, ''),
                    'annee': current_date.year
                })
            
            # Passer au mois suivant
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
    
    context = {
        'resultats': resultats,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
        'classes': classes,
        'mois_disponibles': mois_disponibles,
        'total_ecolages_impayes': total_ecolages_impayes,
        # Conserver les valeurs des filtres pour réaffichage
        'filtre_classe': classe_id,
        'filtre_mois': mois_id,
    }
    return render(request, 'finance/ecolages/liste_impayes.html', context)

@login_required
@user_passes_test(is_admin)
def liste_frais_inscription_impayes(request):
    # Récupérer les paramètres de filtrage
    annee_scolaire_id = request.GET.get('school_year')
    classe_id = request.GET.get('classe')
    
    # Récupérer toutes les années scolaires
    school_years = SchoolYear.objects.all().order_by('-start_date')
    
    # Récupérer l'année scolaire active
    try:
        active_school_year = SchoolYear.objects.get(current=True)
    except SchoolYear.DoesNotExist:
        active_school_year = None
    
    # Récupérer l'année sélectionnée (par défaut l'année active)
    selected_year_id = request.GET.get('school_year')
    if selected_year_id:
        try:
            selected_year = SchoolYear.objects.get(pk=selected_year_id)
        except SchoolYear.DoesNotExist:
            selected_year = active_school_year
    else:
        selected_year = active_school_year
    
    # Récupérer toutes les classes de l'année scolaire sélectionnée
    classes = Class.objects.filter(school_year=selected_year) if selected_year else Class.objects.none()
    
    # Récupérer toutes les inscriptions de l'année scolaire sélectionnée
    inscriptions = Inscription.objects.filter(annee_scolaire=selected_year) if selected_year else Inscription.objects.none()
    
    # Appliquer le filtre de classe si spécifié
    if classe_id:
        inscriptions = inscriptions.filter(classe_demandee_id=classe_id)
    
    # Filtrer pour ne garder que les inscriptions avec des frais d'inscription impayés
    inscriptions_impayees = [
        inscription for inscription in inscriptions 
        if inscription.get_solde() > 0
    ]
    
    # Calculer le nombre total de frais d'inscription impayés
    total_frais_inscription_impayes = len(inscriptions_impayees)
    
    # Calculer le montant total des frais d'inscription impayés
    montant_total_impaye = sum(inscription.get_solde() for inscription in inscriptions_impayees)
    
    context = {
        'inscriptions_impayees': inscriptions_impayees,
        'school_years': school_years,
        'selected_year': selected_year,
        'active_school_year': active_school_year,
        'classes': classes,
        'total_frais_inscription_impayes': total_frais_inscription_impayes,
        'montant_total_impaye': montant_total_impaye,
        # Conserver les valeurs des filtres pour réaffichage
        'filtre_classe': classe_id,
    }
    return render(request, 'finance/frais_inscription/liste_impayes.html', context)