from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import School, SchoolYear, Period, Holiday


def is_admin(user):
    return user.is_authenticated and user.userprofile.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def school_detail(request):
    school, created = School.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        school.name = request.POST.get('name', school.name)
        school.address = request.POST.get('address', school.address)
        school.phone = request.POST.get('phone', school.phone)
        school.email = request.POST.get('email', school.email)
        school.principal_name = request.POST.get('principal_name', school.principal_name)
        
        if 'logo' in request.FILES:
            school.logo = request.FILES['logo']
        
        school.save()
        messages.success(request, 'Informations de l\'établissement mises à jour avec succès!')
        return redirect('school:school_detail')
    
    return render(request, 'school/school_detail.html', {'school': school})

@login_required
@user_passes_test(is_admin)
def school_edit(request):
    school, created = School.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        school.name = request.POST.get('name', school.name)
        school.address = request.POST.get('address', school.address)
        school.phone = request.POST.get('phone', school.phone)
        school.email = request.POST.get('email', school.email)
        school.principal_name = request.POST.get('principal_name', school.principal_name)
        
        if 'logo' in request.FILES:
            school.logo = request.FILES['logo']
        
        school.save()
        messages.success(request, 'Informations de l\'établissement mises à jour avec succès!')
        return redirect('school:school_detail')
    
    return render(request, 'school/school_form.html', {'school': school})

# Vues pour la gestion des années scolaires
@login_required
@user_passes_test(is_admin)
def school_year_list(request):
    school_years = SchoolYear.objects.all().order_by('-start_date')
    return render(request, 'school/school_year_list.html', {'school_years': school_years})

@login_required
@user_passes_test(is_admin)
def school_year_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        current = request.POST.get('current') == 'on'
        
        school_year = SchoolYear.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            current=current
        )
        
        # Si cette année est marquée comme actuelle, désactiver les autres
        if current:
            SchoolYear.objects.exclude(pk=school_year.pk).update(current=False)
        
        messages.success(request, 'Année scolaire créée avec succès!')
        return redirect('school:school_year_list')
    
    return render(request, 'school/school_year_form.html')

@login_required
@user_passes_test(is_admin)
def school_year_detail(request, pk):
    school_year = get_object_or_404(SchoolYear, pk=pk)
    periods = school_year.periods.all()
    holidays = school_year.holidays.all()
    
    return render(request, 'school/school_year_detail.html', {
        'school_year': school_year,
        'periods': periods,
        'holidays': holidays
    })

@login_required
@user_passes_test(is_admin)
def school_year_edit(request, pk):
    school_year = get_object_or_404(SchoolYear, pk=pk)
    
    if request.method == 'POST':
        school_year.name = request.POST.get('name', school_year.name)
        school_year.start_date = request.POST.get('start_date', school_year.start_date)
        school_year.end_date = request.POST.get('end_date', school_year.end_date)
        current = request.POST.get('current') == 'on'
        
        school_year.current = current
        school_year.save()
        
        # Si cette année est marquée comme actuelle, désactiver les autres
        if current:
            SchoolYear.objects.exclude(pk=school_year.pk).update(current=False)
        
        messages.success(request, 'Année scolaire mise à jour avec succès!')
        return redirect('school:school_year_list')
    
    return render(request, 'school/school_year_form.html', {'school_year': school_year})

@login_required
@user_passes_test(is_admin)
def school_year_delete(request, pk):
    school_year = get_object_or_404(SchoolYear, pk=pk)
    
    if request.method == 'POST':
        school_year.delete()
        messages.success(request, 'Année scolaire supprimée avec succès!')
        return redirect('school:school_year_list')
    
    return render(request, 'school/school_year_confirm_delete.html', {'school_year': school_year})

# Vues pour la gestion des périodes
@login_required
@user_passes_test(is_admin)
def period_list(request):
    periods = Period.objects.all().order_by('-start_date')
    return render(request, 'school/period_list.html', {'periods': periods})

@login_required
@user_passes_test(is_admin)
def period_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        school_year_id = request.POST.get('school_year')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        school_year = get_object_or_404(SchoolYear, pk=school_year_id)
        
        Period.objects.create(
            name=name,
            school_year=school_year,
            start_date=start_date,
            end_date=end_date
        )
        
        messages.success(request, 'Période créée avec succès!')
        return redirect('school:period_list')
    
    school_years = SchoolYear.objects.all()
    return render(request, 'school/period_form.html', {'school_years': school_years})

@login_required
@user_passes_test(is_admin)
def period_edit(request, pk):
    period = get_object_or_404(Period, pk=pk)
    
    if request.method == 'POST':
        period.name = request.POST.get('name', period.name)
        school_year_id = request.POST.get('school_year')
        period.start_date = request.POST.get('start_date', period.start_date)
        period.end_date = request.POST.get('end_date', period.end_date)
        
        if school_year_id:
            period.school_year = get_object_or_404(SchoolYear, pk=school_year_id)
        
        period.save()
        messages.success(request, 'Période mise à jour avec succès!')
        return redirect('school:period_list')
    
    school_years = SchoolYear.objects.all()
    return render(request, 'school/period_form.html', {'period': period, 'school_years': school_years})

@login_required
@user_passes_test(is_admin)
def period_delete(request, pk):
    period = get_object_or_404(Period, pk=pk)
    
    if request.method == 'POST':
        period.delete()
        messages.success(request, 'Période supprimée avec succès!')
        return redirect('school:period_list')
    
    return render(request, 'school/period_confirm_delete.html', {'period': period})

# Vues pour la gestion des vacances
@login_required
@user_passes_test(is_admin)
def holiday_list(request):
    holidays = Holiday.objects.all().order_by('-start_date')
    return render(request, 'school/holiday_list.html', {'holidays': holidays})

@login_required
@user_passes_test(is_admin)
def holiday_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        school_year_id = request.POST.get('school_year')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        school_year = get_object_or_404(SchoolYear, pk=school_year_id)
        
        Holiday.objects.create(
            name=name,
            school_year=school_year,
            start_date=start_date,
            end_date=end_date
        )
        
        messages.success(request, 'Vacance créée avec succès!')
        return redirect('school:holiday_list')
    
    school_years = SchoolYear.objects.all()
    return render(request, 'school/holiday_form.html', {'school_years': school_years})

@login_required
@user_passes_test(is_admin)
def holiday_edit(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    
    if request.method == 'POST':
        holiday.name = request.POST.get('name', holiday.name)
        school_year_id = request.POST.get('school_year')
        holiday.start_date = request.POST.get('start_date', holiday.start_date)
        holiday.end_date = request.POST.get('end_date', holiday.end_date)
        
        if school_year_id:
            holiday.school_year = get_object_or_404(SchoolYear, pk=school_year_id)
        
        holiday.save()
        messages.success(request, 'Vacance mise à jour avec succès!')
        return redirect('school:holiday_list')
    
    school_years = SchoolYear.objects.all()
    return render(request, 'school/holiday_form.html', {'holiday': holiday, 'school_years': school_years})

@login_required
@user_passes_test(is_admin)
def holiday_delete(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    
    if request.method == 'POST':
        holiday.delete()
        messages.success(request, 'Vacance supprimée avec succès!')
        return redirect('school:holiday_list')
    
    return render(request, 'school/holiday_confirm_delete.html', {'holiday': holiday})