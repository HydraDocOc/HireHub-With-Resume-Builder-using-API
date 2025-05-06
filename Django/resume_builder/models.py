from django.db import models
from django.conf import settings
from django.urls import reverse , reverse_lazy
from django.contrib.auth.views import LogoutView
from django.core.validators import RegexValidator
from django.contrib import messages

class Resume(models.Model):
    TEMPLATE_CHOICES = [
        ('classic', 'Classic'),
        ('modern', 'Modern'),
        ('professional', 'Professional'),
        ('minimalist', 'Minimalist'),
        ('creative', 'Creative'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=100)
    template = models.CharField(max_length=50, choices=TEMPLATE_CHOICES, default='classic')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} ({self.user.email})"
    
    def get_absolute_url(self):
        return reverse('resume_builder:edit_resume', kwargs={'pk': self.pk})
    
    def get_completion_percentage(self):
        """Calculate how complete the resume is based on filled sections"""
        score = 0
        total = 6  # Total number of main sections
        
        # Check if personal info is filled
        try:
            if self.personal_info:
                score += 1
        except:
            pass
        
        # Check if education info is filled
        if self.education.exists():
            score += 1
        
        # Check if experience info is filled
        if self.experience.exists():
            score += 1
        
        # Check if skills are filled
        if self.skills.exists():
            score += 1
        
        # Check if projects are filled
        if self.projects.exists():
            score += 1
        
        # Check if languages or certificates are filled
        if self.languages.exists() or self.certificates.exists():
            score += 1
        
        return int((score / total) * 100)

class PersonalInfo(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='personal_info')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')]
    )
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)
    summary = models.TextField(blank=True)
    
    def __str__(self):
        return f"Personal info for {self.full_name}"

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    gpa = models.CharField(max_length=10, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-end_date', '-start_date']
    
    def __str__(self):
        return f"{self.position} at {self.company}"

class Skill(models.Model):
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-end_date', '-start_date']
    
    def __str__(self):
        return self.title

class Certificate(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    date_obtained = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-date_obtained']
    
    def __str__(self):
        return f"{self.name} by {self.issuing_organization}"

class Language(models.Model):
    PROFICIENCY_CHOICES = [
        ('elementary', 'Elementary'),
        ('limited_working', 'Limited Working'),
        ('professional_working', 'Professional Working'),
        ('full_professional', 'Full Professional'),
        ('native', 'Native/Bilingual'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
