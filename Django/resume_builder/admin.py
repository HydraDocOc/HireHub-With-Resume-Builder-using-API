from django.contrib import admin
from .models import (
    Resume, PersonalInfo, Education, Experience, 
    Skill, Project, Certificate, Language
)

class PersonalInfoInline(admin.StackedInline):
    model = PersonalInfo
    can_delete = False
    verbose_name_plural = 'Personal Information'

class EducationInline(admin.TabularInline):
    model = Education
    extra = 1

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 3

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class CertificateInline(admin.TabularInline):
    model = Certificate
    extra = 1

class LanguageInline(admin.TabularInline):
    model = Language
    extra = 1

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'template', 'created_at', 'updated_at')
    list_filter = ('template', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username', 'user__email')
    inlines = [
        PersonalInfoInline,
        EducationInline,
        ExperienceInline,
        SkillInline,
        ProjectInline,
        CertificateInline,
        LanguageInline,
    ]