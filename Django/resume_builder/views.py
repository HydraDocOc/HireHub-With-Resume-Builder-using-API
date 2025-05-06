from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, inlineformset_factory
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from .models import (
    Resume, PersonalInfo, Education, Experience, 
    Skill, Project, Certificate, Language
)
from .forms import (
    ResumeForm, PersonalInfoForm, EducationForm, ExperienceForm,
    SkillForm, ProjectForm, CertificateForm, LanguageForm
)
from .utils import generate_pdf

@login_required
def dashboard(request):
    """Display all resumes for the current user"""
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'resume_builder/dashboard.html', {'resumes': resumes})


@login_required
def create_resume(request):
    """Create a new resume"""
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            messages.success(request, 'Resume created successfully! Now let\'s add your personal information.')
            return redirect('resume_builder:edit_personal_info', pk=resume.pk)
    else:
        form = ResumeForm()
    
    return render(request, 'resume_builder/create_resume.html', {'form': form})

@login_required
def edit_resume(request, pk):
    """Edit resume details"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resume updated successfully!')
            return redirect('resume_builder:edit_resume', pk=resume.pk)
    else:
        form = ResumeForm(instance=resume)
    
    return render(request, 'resume_builder/edit_resume.html', {'form': form, 'resume': resume})

@login_required
def edit_personal_info(request, pk):
    """Edit personal information for a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    # Create a formset for PersonalInfo with only one form
    PersonalInfoFormSet = inlineformset_factory(
        Resume, PersonalInfo,
        form=PersonalInfoForm,
        extra=1 if not hasattr(resume, 'personal_info') else 0,
        max_num=1,
        can_delete=False,  # Disable deletion since it's required
        exclude=['resume'],  # Exclude resume field since it's handled by formset
    )
    
    if request.method == 'POST':
        formset = PersonalInfoFormSet(request.POST, instance=resume)
        if formset.is_valid():
            try:
                instances = formset.save(commit=False)
                for instance in instances:
                    # Clean the phone number by removing any non-digit characters
                    if instance.phone:
                        instance.phone = ''.join(filter(str.isdigit, instance.phone))
                    instance.save()
                formset.save_m2m()
                
                messages.success(request, 'Personal information updated successfully!')
                return redirect('resume_builder:edit_education', pk=resume.pk)
            except Exception as e:
                print(f"Error saving personal info: {str(e)}")
                messages.error(request, 'An error occurred while saving your information.')
        else:
            # Log formset errors for debugging
            print(formset.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        formset = PersonalInfoFormSet(instance=resume)
    
    context = {
        'formset': formset, 
        'resume': resume,
        'section_title': 'Personal Information',
        'section_description': 'Update your contact details and summary',
        'item_name': 'Profile',
        'active_step': 'personal_info',
    }
    
    return render(request, 'resume_builder/edit_personal_info.html', context)



@login_required
def edit_education(request, pk):
    """Edit education entries for a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    EducationFormSet = inlineformset_factory(
        Resume, Education,
        form=EducationForm,
        extra=1,
        can_delete=True,
    )
    
    if request.method == 'POST':
        formset = EducationFormSet(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Education information updated successfully!')
            return redirect('resume_builder:edit_experience', pk=resume.pk)
    else:
        formset = EducationFormSet(instance=resume)
    
    context = {
        'formset': formset, 
        'resume': resume,
        'section_title': 'Education',
        'section_description': 'Add your educational background, starting with the most recent',
        'item_name': 'Education',
        'active_step': 'education',
        'prev_url': reverse('resume_builder:edit_personal_info', kwargs={'pk': resume.pk}),
        'prev_title': 'Personal Information'
    }
    
    return render(request, 'resume_builder/edit_education.html', context)

@login_required
def edit_experience(request, pk):
    """Edit experience entries for a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    ExperienceFormSet = inlineformset_factory(
        Resume, Experience,
        form=ExperienceForm,
        extra=1,
        can_delete=True,
    )
    
    if request.method == 'POST':
        formset = ExperienceFormSet(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Experience information updated successfully!')
            return redirect('resume_builder:edit_skills', pk=resume.pk)
    else:
        formset = ExperienceFormSet(instance=resume)
    
    context = {
        'formset': formset, 
        'resume': resume,
        'section_title': 'Experience',
        'section_description': 'Add your work experience, starting with the most recent',
        'item_name': 'Experience',
        'active_step': 'experience',
        'prev_url': reverse('resume_builder:edit_education', kwargs={'pk': resume.pk}),
        'prev_title': 'Education'
    }
    
    return render(request, 'resume_builder/edit_experience.html', context)

@login_required
def edit_skills(request, pk):
    """Edit skills for a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    SkillFormSet = inlineformset_factory(
        Resume, Skill,
        form=SkillForm,
        extra=3,
        can_delete=True,
    )
    
    if request.method == 'POST':
        formset = SkillFormSet(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Skills updated successfully!')
            return redirect('resume_builder:edit_projects', pk=resume.pk)
    else:
        formset = SkillFormSet(instance=resume)
    
    context = {
        'formset': formset, 
        'resume': resume,
        'section_title': 'Skills',
        'section_description': 'Add your technical and soft skills with proficiency levels',
        'item_name': 'Skill',
        'active_step': 'skills',
        'prev_url': reverse('resume_builder:edit_experience', kwargs={'pk': resume.pk}),
        'prev_title': 'Experience'
    }
    
    return render(request, 'resume_builder/edit_skills.html', context)

@login_required
def edit_projects(request, pk):
    """Edit projects for a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    ProjectFormSet = inlineformset_factory(
        Resume, Project,
        form=ProjectForm,
        extra=1,
        can_delete=True,
    )
    
    if request.method == 'POST':
        formset = ProjectFormSet(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Projects updated successfully!')
            return redirect('resume_builder:edit_certificates', pk=resume.pk)
    else:
        formset = ProjectFormSet(instance=resume)
    
    context = {
        'formset': formset, 
        'resume': resume,
        'section_title': 'Projects',
        'section_description': 'Add your significant projects with descriptions and links',
        'item_name': 'Project',
        'active_step': 'projects',
        'prev_url': reverse('resume_builder:edit_skills', kwargs={'pk': resume.pk}),
        'prev_title': 'Skills'
    }
    
    return render(request, 'resume_builder/edit_projects.html', context)

@login_required
def edit_certificates(request, pk):
    """Edit certificates for a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    CertificateFormSet = inlineformset_factory(
        Resume, Certificate,
        form=CertificateForm,
        extra=1,
        can_delete=True,
    )
    
    if request.method == 'POST':
        formset = CertificateFormSet(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Certificates updated successfully!')
            return redirect('resume_builder:edit_languages', pk=resume.pk)
    else:
        formset = CertificateFormSet(instance=resume)
    
    context = {
        'formset': formset, 
        'resume': resume,
        'section_title': 'Certificates',
        'section_description': 'Add professional certifications you have earned',
        'item_name': 'Certificate',
        'active_step': 'certificates',
        'prev_url': reverse('resume_builder:edit_projects', kwargs={'pk': resume.pk}),
        'prev_title': 'Projects'
    }
    
    return render(request, 'resume_builder/edit_certificates.html', context)

@login_required
def edit_languages(request, pk):
    """Edit languages for a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    LanguageFormSet = inlineformset_factory(
        Resume, Language,
        form=LanguageForm,
        extra=1,
        can_delete=True,
    )
    
    if request.method == 'POST':
        formset = LanguageFormSet(request.POST, instance=resume)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Languages updated successfully!')
            return redirect('resume_builder:preview_resume', pk=resume.pk)
    else:
        formset = LanguageFormSet(instance=resume)
    
    context = {
        'formset': formset, 
        'resume': resume,
        'section_title': 'Languages',
        'section_description': 'Add languages you know and your proficiency level',
        'item_name': 'Language',
        'active_step': 'languages',
        'prev_url': reverse('resume_builder:edit_certificates', kwargs={'pk': resume.pk}),
        'prev_title': 'Certificates'
    }
    
    return render(request, 'resume_builder/edit_languages.html', context)

@login_required
def preview_resume(request, pk):
    """Preview the resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    # Check if we want to render the HTML content directly (for iframe)
    if request.GET.get('format') == 'html':
        template_path = f'resume_builder/resume_templates/{resume.template}.html'
        return render(request, template_path, {'resume': resume})
    
    return render(request, 'resume_builder/preview_resume.html', {'resume': resume})

@login_required
def download_resume(request, pk):
    """Show coming soon page for PDF download"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    return render(request, 'resume_builder/coming_soon.html', {'resume': resume})

@login_required
def delete_resume(request, pk):
    """Delete a resume"""
    resume = get_object_or_404(Resume, pk=pk)
    
    # Check if the current user is the owner of the resume
    if resume.user != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        resume_title = resume.title
        resume.delete()
        messages.success(request, f'Your resume "{resume_title}" has been deleted.')
        return redirect('resume_builder:dashboard')
    
    return render(request, 'resume_builder/delete_resume.html', {'resume': resume})

