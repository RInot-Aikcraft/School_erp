from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, ParentStudentRelationship

# Liste complète des pays du monde
COUNTRIES = [
    ('AF', 'Afghanistan'),
    ('ZA', 'Afrique du Sud'),
    ('AL', 'Albanie'),
    ('DZ', 'Algérie'),
    ('DE', 'Allemagne'),
    ('AD', 'Andorre'),
    ('AO', 'Angola'),
    ('AI', 'Anguilla'),
    ('AQ', 'Antarctique'),
    ('AG', 'Antigua-et-Barbuda'),
    ('SA', 'Arabie Saoudite'),
    ('AR', 'Argentine'),
    ('AM', 'Arménie'),
    ('AW', 'Aruba'),
    ('AU', 'Australie'),
    ('AT', 'Autriche'),
    ('AZ', 'Azerbaïdjan'),
    ('BS', 'Bahamas'),
    ('BH', 'Bahreïn'),
    ('BD', 'Bangladesh'),
    ('BB', 'Barbade'),
    ('BE', 'Belgique'),
    ('BZ', 'Belize'),
    ('BJ', 'Bénin'),
    ('BM', 'Bermudes'),
    ('BT', 'Bhoutan'),
    ('BY', 'Biélorussie'),
    ('BO', 'Bolivie'),
    ('BQ', 'Bonaire, Saint-Eustache et Saba'),
    ('BA', 'Bosnie-Herzégovine'),
    ('BW', 'Botswana'),
    ('BR', 'Brésil'),
    ('BN', 'Brunei'),
    ('BG', 'Bulgarie'),
    ('BF', 'Burkina Faso'),
    ('BI', 'Burundi'),
    ('KH', 'Cambodge'),
    ('CM', 'Cameroun'),
    ('CA', 'Canada'),
    ('CV', 'Cap-Vert'),
    ('CL', 'Chili'),
    ('CN', 'Chine'),
    ('CY', 'Chypre'),
    ('CO', 'Colombie'),
    ('KM', 'Comores'),
    ('CG', 'Congo-Brazzaville'),
    ('CD', 'Congo-Kinshasa'),
    ('KP', 'Corée du Nord'),
    ('KR', 'Corée du Sud'),
    ('CR', 'Costa Rica'),
    ('CI', "Côte d'Ivoire"),
    ('HR', 'Croatie'),
    ('CU', 'Cuba'),
    ('CW', 'Curaçao'),
    ('DK', 'Danemark'),
    ('DJ', 'Djibouti'),
    ('DM', 'Dominique'),
    ('EG', 'Égypte'),
    ('AE', 'Émirats arabes unis'),
    ('EC', 'Équateur'),
    ('ER', 'Érythrée'),
    ('ES', 'Espagne'),
    ('EE', 'Estonie'),
    ('SZ', 'Eswatini'),
    ('US', 'États-Unis'),
    ('ET', 'Éthiopie'),
    ('FJ', 'Fidji'),
    ('FI', 'Finlande'),
    ('FR', 'France'),
    ('GA', 'Gabon'),
    ('GM', 'Gambie'),
    ('GE', 'Géorgie'),
    ('GS', 'Géorgie du Sud-et-les Îles Sandwich du Sud'),
    ('GH', 'Ghana'),
    ('GI', 'Gibraltar'),
    ('GR', 'Grèce'),
    ('GD', 'Grenade'),
    ('GL', 'Groenland'),
    ('GP', 'Guadeloupe'),
    ('GU', 'Guam'),
    ('GT', 'Guatemala'),
    ('GG', 'Guernesey'),
    ('GN', 'Guinée'),
    ('GQ', 'Guinée équatoriale'),
    ('GW', 'Guinée-Bissau'),
    ('GY', 'Guyana'),
    ('GF', 'Guyane française'),
    ('HT', 'Haïti'),
    ('HN', 'Honduras'),
    ('HU', 'Hongrie'),
    ('BV', 'Île Bouvet'),
    ('CX', 'Île Christmas'),
    ('IM', 'Île de Man'),
    ('NF', 'Île Norfolk'),
    ('KY', 'Îles Caïmans'),
    ('CC', 'Îles Cocos'),
    ('CK', 'Îles Cook'),
    ('FO', 'Îles Féroé'),
    ('FK', 'Îles Malouines'),
    ('MP', 'Îles Mariannes du Nord'),
    ('MH', 'Îles Marshall'),
    ('UM', 'Îles mineures éloignées des États-Unis'),
    ('PN', 'Îles Pitcairn'),
    ('SB', 'Îles Salomon'),
    ('TC', 'Îles Turques-et-Caïques'),
    ('VG', 'Îles Vierges britanniques'),
    ('VI', 'Îles Vierges des États-Unis'),
    ('IN', 'Inde'),
    ('ID', 'Indonésie'),
    ('IQ', 'Irak'),
    ('IR', 'Iran'),
    ('IE', 'Irlande'),
    ('IS', 'Islande'),
    ('IL', 'Israël'),
    ('IT', 'Italie'),
    ('JM', 'Jamaïque'),
    ('JP', 'Japon'),
    ('JE', 'Jersey'),
    ('JO', 'Jordanie'),
    ('KZ', 'Kazakhstan'),
    ('KE', 'Kenya'),
    ('KG', 'Kirghizistan'),
    ('KI', 'Kiribati'),
    ('KW', 'Koweït'),
    ('RE', 'La Réunion'),
    ('LA', 'Laos'),
    ('LS', 'Lesotho'),
    ('LV', 'Lettonie'),
    ('LB', 'Liban'),
    ('LR', 'Libéria'),
    ('LY', 'Libye'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Lituanie'),
    ('LU', 'Luxembourg'),
    ('MK', 'Macédoine du Nord'),
    ('MG', 'Madagascar'),
    ('MY', 'Malaisie'),
    ('MW', 'Malawi'),
    ('MV', 'Maldives'),
    ('ML', 'Mali'),
    ('MT', 'Malte'),
    ('MA', 'Maroc'),
    ('MQ', 'Martinique'),
    ('MU', 'Maurice'),
    ('MR', 'Mauritanie'),
    ('YT', 'Mayotte'),
    ('MX', 'Mexique'),
    ('FM', 'Micronésie'),
    ('MD', 'Moldavie'),
    ('MC', 'Monaco'),
    ('MN', 'Mongolie'),
    ('ME', 'Monténégro'),
    ('MS', 'Montserrat'),
    ('MZ', 'Mozambique'),
    ('MM', 'Myanmar'),
    ('NA', 'Namibie'),
    ('NR', 'Nauru'),
    ('NP', 'Népal'),
    ('NI', 'Nicaragua'),
    ('NE', 'Niger'),
    ('NG', 'Nigeria'),
    ('NU', 'Niue'),
    ('NO', 'Norvège'),
    ('NC', 'Nouvelle-Calédonie'),
    ('NZ', 'Nouvelle-Zélande'),
    ('OM', 'Oman'),
    ('UG', 'Ouganda'),
    ('UZ', 'Ouzbékistan'),
    ('PK', 'Pakistan'),
    ('PW', 'Palaos'),
    ('PA', 'Panama'),
    ('PG', 'Papouasie-Nouvelle-Guinée'),
    ('PY', 'Paraguay'),
    ('NL', 'Pays-Bas'),
    ('PH', 'Philippines'),
    ('PL', 'Pologne'),
    ('PF', 'Polynésie française'),
    ('PR', 'Porto Rico'),
    ('PT', 'Portugal'),
    ('QA', 'Qatar'),
    ('HK', 'R.A.S. chinoise de Hong Kong'),
    ('MO', 'R.A.S. chinoise de Macao'),
    ('CF', 'République centrafricaine'),
    ('DO', 'République dominicaine'),
    ('CZ', 'République tchèque'),
    ('RO', 'Roumanie'),
    ('GB', 'Royaume-Uni'),
    ('RU', 'Russie'),
    ('RW', 'Rwanda'),
    ('EH', 'Sahara occidental'),
    ('BL', 'Saint-Barthélemy'),
    ('KN', 'Saint-Christophe-et-Niévès'),
    ('SM', 'Saint-Marin'),
    ('PM', 'Saint-Pierre-et-Miquelon'),
    ('VC', 'Saint-Vincent-et-les Grenadines'),
    ('SH', 'Sainte-Hélène, Ascension et Tristan da Cunha'),
    ('LC', 'Sainte-Lucie'),
    ('SV', 'Salvador'),
    ('WS', 'Samoa'),
    ('AS', 'Samoa américaines'),
    ('ST', 'Sao Tomé-et-Principe'),
    ('SN', 'Sénégal'),
    ('RS', 'Serbie'),
    ('SC', 'Seychelles'),
    ('SL', 'Sierra Leone'),
    ('SG', 'Singapour'),
    ('SK', 'Slovaquie'),
    ('SI', 'Slovénie'),
    ('SO', 'Somalie'),
    ('SD', 'Soudan'),
    ('SS', 'Soudan du Sud'),
    ('LK', 'Sri Lanka'),
    ('SE', 'Suède'),
    ('CH', 'Suisse'),
    ('SR', 'Suriname'),
    ('SJ', 'Svalbard et Jan Mayen'),
    ('SY', 'Syrie'),
    ('TJ', 'Tadjikistan'),
    ('TW', 'Taïwan'),
    ('TZ', 'Tanzanie'),
    ('TD', 'Tchad'),
    ('TF', 'Terres australes françaises'),
    ('TH', 'Thaïlande'),
    ('TL', 'Timor oriental'),
    ('TG', 'Togo'),
    ('TK', 'Tokelau'),
    ('TO', 'Tonga'),
    ('TT', 'Trinité-et-Tobago'),
    ('TN', 'Tunisie'),
    ('TM', 'Turkménistan'),
    ('TR', 'Turquie'),
    ('TV', 'Tuvalu'),
    ('UA', 'Ukraine'),
    ('UY', 'Uruguay'),
    ('VU', 'Vanuatu'),
    ('VA', 'Vatican'),
    ('VE', 'Venezuela'),
    ('VN', 'Viêt Nam'),
    ('WF', 'Wallis-et-Futuna'),
    ('YE', 'Yémen'),
    ('ZM', 'Zambie'),
    ('ZW', 'Zimbabwe'),
]

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Adresse e-mail",
        help_text="Veuillez saisir une adresse e-mail valide."
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Prénom"
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nom"
    )
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPES,
        required=True,
        label="Type d'utilisateur"
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Téléphone",
        help_text="Format: +261 XX XX XXX XX"
    )
    address = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Adresse"
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date de naissance"
    )
    
    # Champs supplémentaires pour tous les utilisateurs
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        required=False,
        label="Genre"
    )
    place_of_birth = forms.CharField(
        max_length=100,
        required=False,
        label="Lieu de naissance"
    )
    nationality = forms.ChoiceField(  # Changé de CharField à ChoiceField
        choices=COUNTRIES,  # Utilisation de la liste des pays
        required=False,
        label="Nationalité",
        help_text="Sélectionnez votre pays de nationalité"
    )
    id_card_number = forms.CharField(
        max_length=50,
        required=False,
        label="Numéro CIN / Passeport"
    )
    civil_status = forms.ChoiceField(
        choices=UserProfile.CIVIL_STATUS_CHOICES,
        required=False,
        label="Situation civile"
    )
    emergency_contact_name = forms.CharField(
        max_length=100,
        required=False,
        label="Nom du contact d'urgence"
    )
    emergency_contact_relationship = forms.CharField(
        max_length=50,
        required=False,
        label="Relation avec le contact d'urgence"
    )
    emergency_contact_phone = forms.CharField(
        max_length=20,
        required=False,
        label="Téléphone du contact d'urgence"
    )
    
    # Champs spécifiques aux enseignants
    internal_id = forms.CharField(
        max_length=50,
        required=False,
        label="Matricule interne",
        help_text="Identifiant interne attribué par l'établissement"
    )
    professional_id = forms.CharField(
        max_length=50,
        required=False,
        label="ID professionnel",
        help_text="Numéro d'identification professionnelle"
    )
    diplomas = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Diplômes et formations",
        help_text="Liste des diplômes et formations suivies"
    )
    hire_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date d'embauche"
    )
    position = forms.CharField(
        max_length=100,
        required=False,
        label="Poste occupé"
    )
    employment_status = forms.ChoiceField(
        choices=UserProfile.EMPLOYMENT_STATUS_CHOICES,
        required=False,
        label="Statut d'emploi"
    )
    experience_years = forms.IntegerField(
        required=False,
        min_value=0,
        label="Années d'expérience",
        help_text="Nombre total d'années d'expérience professionnelle"
    )
    previous_positions = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Expériences professionnelles précédentes",
        help_text="Postes occupés précédemment avec les périodes"
    )
    
    # Champs spécifiques aux parents
    number_of_children = forms.IntegerField(
        required=False,
        min_value=0,
        label="Nombre d'enfants"
    )
    occupation = forms.CharField(
        max_length=100,
        required=False,
        label="Profession"
    )
    employer = forms.CharField(
        max_length=100,
        required=False,
        label="Employeur"
    )
    work_phone = forms.CharField(
        max_length=20,
        required=False,
        label="Téléphone professionnel"
    )
    
    # Champs spécifiques aux élèves
    student_id = forms.CharField(
        max_length=50,
        required=False,
        label="Numéro d'étudiant",
        help_text="Identifiant unique attribué à l'étudiant"
    )
    blood_type = forms.CharField(
        max_length=5,
        required=False,
        label="Groupe sanguin",
        help_text="Ex: A+, B-, O+, AB+"
    )
    allergies = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Allergies",
        help_text="Veuillez lister toutes les allergies connues"
    )
    medical_conditions = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Conditions médicales",
        help_text="Veuillez indiquer toute condition médicale pertinente"
    )
    previous_school = forms.CharField(
        max_length=100,
        required=False,
        label="École précédente"
    )
    previous_school_address = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Adresse de l'école précédente"
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type', 
                  'phone', 'address', 'date_of_birth', 'gender', 'place_of_birth', 'nationality', 
                  'id_card_number', 'civil_status', 'emergency_contact_name', 
                  'emergency_contact_relationship', 'emergency_contact_phone', 'internal_id', 
                  'professional_id', 'diplomas', 'hire_date', 'position', 'employment_status', 
                  'experience_years', 'previous_positions', 'number_of_children', 'occupation', 
                  'employer', 'work_phone', 'student_id', 'blood_type', 'allergies', 
                  'medical_conditions', 'previous_school', 'previous_school_address')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les messages d'aide des champs de mot de passe
        self.fields['username'].help_text = "Requis. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ uniquement."
        self.fields['password1'].help_text = "Votre mot de passe doit contenir au moins 8 caractères."
        self.fields['password2'].help_text = "Entrez le même mot de passe pour vérification."
        
        # Ajouter une option vide pour le champ nationalité
        self.fields['nationality'].choices = [('', 'Sélectionnez un pays')] + list(self.fields['nationality'].choices)
    
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
            
            # Informations professionnelles (pour les enseignants)
            user_profile.internal_id = self.cleaned_data['internal_id']
            user_profile.professional_id = self.cleaned_data['professional_id']
            user_profile.diplomas = self.cleaned_data['diplomas']
            user_profile.hire_date = self.cleaned_data['hire_date']
            user_profile.position = self.cleaned_data['position']
            user_profile.employment_status = self.cleaned_data['employment_status']
            user_profile.experience_years = self.cleaned_data['experience_years']
            user_profile.previous_positions = self.cleaned_data['previous_positions']
            
            # Informations spécifiques aux parents
            user_profile.number_of_children = self.cleaned_data['number_of_children']
            user_profile.occupation = self.cleaned_data['occupation']
            user_profile.employer = self.cleaned_data['employer']
            user_profile.work_phone = self.cleaned_data['work_phone']
            
            # Informations spécifiques aux élèves
            user_profile.student_id = self.cleaned_data['student_id']
            user_profile.blood_type = self.cleaned_data['blood_type']
            user_profile.allergies = self.cleaned_data['allergies']
            user_profile.medical_conditions = self.cleaned_data['medical_conditions']
            user_profile.previous_school = self.cleaned_data['previous_school']
            user_profile.previous_school_address = self.cleaned_data['previous_school_address']
            
            user_profile.save()
        return user

# Formulaire spécifique pour les parents
class ParentCreationForm(CustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].initial = 'parent'
        self.fields['user_type'].widget = forms.HiddenInput()

# Formulaire spécifique pour les élèves

class StudentCreationForm(CustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Définir la valeur initiale et marquer le champ comme non requis
        self.fields['user_type'].initial = 'student'
        self.fields['user_type'].required = False
        
    def clean_user_type(self):
        # S'assurer que le type d'utilisateur est bien 'student'
        return 'student'
    
    def save(self, commit=True):
        # Forcer le type d'utilisateur à 'student' avant de sauvegarder
        self.instance.user_type = 'student'
        return super().save(commit=commit)
    
# Dans auth_app/forms.py
class ParentStudentRelationshipForm(forms.ModelForm):
    class Meta:
        model = ParentStudentRelationship
        fields = ['parent', 'relationship_type', 'is_primary_contact', 'has_pickup_rights', 'notes']
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'relationship_type': forms.Select(attrs={'class': 'form-select'}),
            'is_primary_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_pickup_rights': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les parents pour n'afficher que ceux qui ne sont pas déjà associés à cet élève
        if student:
            existing_parents = ParentStudentRelationship.objects.filter(student=student).values_list('parent_id', flat=True)
            self.fields['parent'].queryset = User.objects.filter(
                userprofile__user_type='parent'
            ).exclude(
                id__in=existing_parents
            )