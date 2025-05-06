import requests
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import (
    CustomUser, Company, Job
)

class UserLoginForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=[('user', 'User'), ('admin', 'Admin')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'role']

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'mobile', 'password', 'confirm_password']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'logo_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'company', 'location', 'salary_range', 'job_type', 'requirements']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
        }

class JobPostForm(forms.ModelForm):
    company = forms.ChoiceField(choices=[], label="Company")  # Will be populated dynamically
    
    class Meta:
        model = Job
        fields = ['title', 'company', 'description', 'location', 
                 'salary_range', 'job_type', 'requirements']
        widgets = {
            'title': forms.TextInput(attrs={'id': 'id_title', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'id': 'id_description', 'rows': 5, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'id': 'id_location', 'class': 'form-control'}),
            'salary_range': forms.TextInput(attrs={'id': 'id_salary_range', 'class': 'form-control', 'placeholder': 'e.g. ₹80,000 - ₹1,00,000'}),
            'job_type': forms.Select(attrs={'id': 'id_job_type', 'class': 'form-select'}, choices=[
                ('Full-time', 'Full-time'),
                ('Part-time', 'Part-time'),
                ('Contract', 'Contract'),
                ('Remote', 'Remote'),
            ]),
            'requirements': forms.Textarea(attrs={'id': 'id_requirements', 'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            response = requests.get(f"{settings.FLASK_API_BASE}/companies")
            if response.status_code == 200:
                companies = response.json()
                self.fields['company'].choices = [
                    (company['id'], company['name']) for company in companies
                ]
        except requests.RequestException:
            self.fields['company'].choices = []

class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Job title or keyword',
        'class': 'form-control'
    }))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Location',
        'class': 'form-control'
    }))

