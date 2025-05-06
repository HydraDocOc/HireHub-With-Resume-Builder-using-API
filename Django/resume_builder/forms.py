from django import forms
from django.core.validators import RegexValidator
from .models import (
    Resume, PersonalInfo, Education, Experience, 
    Skill, Project, Certificate, Language
)

# Template choices for the resume form
TEMPLATE_CHOICES = [
    ('classic', 'Classic'),
    ('modern', 'Modern'),
    ('professional', 'Professional'),
    ('minimalist', 'Minimalist'),
    ('creative', 'Creative'),
]

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'template']
        widgets = {
            'template': forms.Select(choices=TEMPLATE_CHOICES),
        }

class PersonalInfoForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')],
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]{10}',
            'title': 'Please enter exactly 10 digits',
            'maxlength': '10',
            'minlength': '10'
        })
    )

    class Meta:
        model = PersonalInfo
        fields = '__all__'
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
            return phone
        return phone

    def clean(self):
        cleaned_data = super().clean()
        # Add any additional validation here
        return cleaned_data
    
    
class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ['resume', 'order']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ['resume', 'order']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        exclude = ['resume', 'order']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['resume', 'order']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        exclude = ['resume', 'order']
        widgets = {
            'date_obtained': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        exclude = ['resume', 'order']