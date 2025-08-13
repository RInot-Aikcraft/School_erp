from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import FeeType, FeeStructure, Fee, PaymentMethod, Payment
from .forms import FeeTypeForm, FeeStructureForm, PaymentMethodForm, PaymentForm
from academics.models import Class  # Correction: import depuis academics.models

# Vues pour les types de frais
@login_required
def fee_type_list(request):
    fee_types = FeeType.objects.all()
    return render(request, 'finance/fee_type_list.html', {'fee_types': fee_types})

@login_required
def fee_type_create(request):
    if request.method == 'POST':
        form = FeeTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de frais créé avec succès.')
            return redirect('finance:fee_type_list')
    else:
        form = FeeTypeForm()
    return render(request, 'finance/fee_type_form.html', {'form': form})

# Vues pour les structures de frais
@login_required
def fee_structure_list(request):
    fee_structures = FeeStructure.objects.all()
    return render(request, 'finance/fee_structure_list.html', {'fee_structures': fee_structures})

@login_required
def fee_structure_create(request):
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Structure de frais créée avec succès.')
            return redirect('finance:fee_structure_list')
    else:
        form = FeeStructureForm()
    return render(request, 'finance/fee_structure_form.html', {'form': form})

# Vues pour les frais des élèves
@login_required
def fee_list(request):
    fees = Fee.objects.all()
    return render(request, 'finance/fee_list.html', {'fees': fees})

@login_required
def student_fee_list(request, student_id):
    fees = Fee.objects.filter(student_id=student_id)
    return render(request, 'finance/student_fee_list.html', {'fees': fees})

# Vues pour les paiements
@login_required
def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'finance/payment_list.html', {'payments': payments})

@login_required
def payment_create(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.fee = fee
            payment.save()
            
            # Mettre à jour le montant payé et le statut du frais
            fee.amount_paid += payment.amount
            fee.save()
            
            messages.success(request, 'Paiement enregistré avec succès.')
            return redirect('finance:student_fee_list', student_id=fee.student.id)
    else:
        form = PaymentForm()
    return render(request, 'finance/payment_form.html', {'form': form, 'fee': fee})

# Vue pour générer les frais pour une classe
@login_required
def generate_fees_for_class(request, class_id):  # Correction: renommé de classroom_id à class_id
    classroom = Class.objects.get(id=class_id)  # Correction: utiliser Class au lieu de Classroom
    fee_structures = FeeStructure.objects.filter(classroom=classroom)
    
    # Récupérer tous les étudiants de cette classe
    from auth_app.models import CustomUser
    students = CustomUser.objects.filter(role='student', student_classroom=classroom)
    
    # Créer les frais pour chaque étudiant
    for student in students:
        for fee_structure in fee_structures:
            # Vérifier si le frais existe déjà pour éviter les doublons
            if not Fee.objects.filter(student=student, fee_structure=fee_structure).exists():
                Fee.objects.create(
                    student=student,
                    fee_structure=fee_structure,
                    amount_due=fee_structure.amount,
                    balance=fee_structure.amount
                )
    
    messages.success(request, f'Frais générés avec succès pour la classe {classroom.name}.')
    return redirect('finance:fee_list')