from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from academics.models import Subject, TeacherSubject

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPES, required=True)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    # Champs supplémentaires pour les enseignants
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=False)
    place_of_birth = forms.CharField(max_length=100, required=False)
    nationality = forms.CharField(max_length=50, required=False)
    id_card_number = forms.CharField(max_length=50, required=False)
    civil_status = forms.ChoiceField(choices=UserProfile.CIVIL_STATUS_CHOICES, required=False)
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    emergency_contact_relationship = forms.CharField(max_length=50, required=False)
    emergency_contact_phone = forms.CharField(max_length=20, required=False)
    
    internal_id = forms.CharField(max_length=50, required=False)
    professional_id = forms.CharField(max_length=50, required=False)
    diplomas = forms.CharField(widget=forms.Textarea, required=False)
    hire_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    position = forms.CharField(max_length=100, required=False)
    employment_status = forms.ChoiceField(choices=UserProfile.EMPLOYMENT_STATUS_CHOICES, required=False)
    experience_years = forms.IntegerField(required=False, min_value=0)
    previous_positions = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type', 
                  'phone', 'address', 'date_of_birth', 'gender', 'place_of_birth', 'nationality', 
                  'id_card_number', 'civil_status', 'emergency_contact_name', 
                  'emergency_contact_relationship', 'emergency_contact_phone', 'internal_id', 
                  'professional_id', 'diplomas', 'hire_date', 'position', 'employment_status', 
                  'experience_years', 'previous_positions')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            user_profile = UserProfile.objects.get(user=user)
            user_profile.user_type = self.cleaned_data['user_type']
            user_profile.phone = self.cleaned_data['phone']
            user_profile.address = self.cleaned_data['address']
            user_profile.date_of_birth = self.cleaned_data['date_of_birth']
            
            # Informations personnelles supplémentaires
            user_profile.gender = self.cleaned_data['gender']
            user_profile.place_of_birth = self.cleaned_data['place_of_birth']
            user_profile.nationality = self.cleaned_data['nationality']
            user_profile.id_card_number = self.cleaned_data['id_card_number']
            user_profile.civil_status = self.cleaned_data['civil_status']
            user_profile.emergency_contact_name = self.cleaned_data['emergency_contact_name']
            user_profile.emergency_contact_relationship = self.cleaned_data['emergency_contact_relationship']
            user_profile.emergency_contact_phone = self.cleaned_data['emergency_contact_phone']
            
            # Informations professionnelles
            user_profile.internal_id = self.cleaned_data['internal_id']
            user_profile.professional_id = self.cleaned_data['professional_id']
            user_profile.diplomas = self.cleaned_data['diplomas']
            user_profile.hire_date = self.cleaned_data['hire_date']
            user_profile.position = self.cleaned_data['position']
            user_profile.employment_status = self.cleaned_data['employment_status']
            user_profile.experience_years = self.cleaned_data['experience_years']
            user_profile.previous_positions = self.cleaned_data['previous_positions']
            
            user_profile.save()
        return user