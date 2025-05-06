import requests
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, FormView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden 
from django.contrib.auth import logout
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.conf import settings

from .models import CustomUser , Company
from .forms import (
    UserRegisterForm, UserLoginForm, CompanyForm, JobPostForm, SearchForm,
)

# API base URL from settings
FLASK_API_BASE = settings.FLASK_API_BASE

class IndexView(View):
    def get(self, request):
        try:
            response = requests.get(f"{FLASK_API_BASE}/jobs")
            jobs = response.json() if response.status_code == 200 else []
        except requests.RequestException as e:
            jobs = []
            messages.error(request, f"Error connecting to API: {str(e)}")

        context = {
            'jobs': jobs,
            'search_form': SearchForm()
        }
        return render(request, 'jobs/index.html', context)

class JobDetailView(View):
    def get(self, request, pk):
        try:
            response = requests.get(f"{FLASK_API_BASE}/job/{pk}")
            job = response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            job = None
            messages.error(request, f"Error connecting to API: {str(e)}")

        if not job:
            return render(request, 'jobs/error.html', {
                'error_code': 404,
                'error_message': 'Job Not Found',
                'error_description': 'This job does not exist or has been removed.'
            }, status=404)

        return render(request, 'jobs/job_detail.html', {'job': job})

class CompanyProfileView(View):
    model = Company
    def get(self, request, pk):
        try:
            response = requests.get(f"{FLASK_API_BASE}/company/{pk}")
            company = response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            company = None
            messages.error(request, f"Error connecting to API: {str(e)}")

        if not company:
            return render(request, 'jobs/error.html', {
                'error_code': 404,
                'error_message': 'Company Not Found',
                'error_description': 'This company does not exist or has been removed.'
            }, status=404)

        return render(request, 'jobs/company_profile.html', {'company': company})

class SearchView(View):
    def get(self, request):
        keyword = request.GET.get('keyword', '').strip()
        location = request.GET.get('location', '').strip()
        
        try:
            response = requests.get(f"{FLASK_API_BASE}/jobs")
            jobs = response.json() if response.status_code == 200 else []
        except requests.RequestException as e:
            jobs = []
            messages.error(request, f"Error connecting to API: {str(e)}")

        # Filter on Django side if Flask doesn't yet support query params
        if keyword:
            jobs = [job for job in jobs if keyword.lower() in job['title'].lower() or keyword.lower() in job['description'].lower()]
        if location:
            jobs = [job for job in jobs if location.lower() in job['location'].lower()]

        context = {
            'jobs': jobs,
            'search_form': SearchForm(initial={'keyword': keyword, 'location': location}),
            'search_keyword': keyword,
            'search_location': location
        }

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('jobs/_jobs_list.html', context, request=request)
            return JsonResponse({'html': html})

        return render(request, 'jobs/index.html', context)

class CustomLoginView(LoginView):
    template_name = 'jobs/login.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.role != form.cleaned_data.get('role'):
            form.add_error(None, "Invalid role selection for this account.")
            return self.form_invalid(form)
        messages.success(self.request, "Login successful!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('job_portal:dashboard')

class RegisterView(FormView):
    template_name = 'jobs/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('job_portal:login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Registration successful! Please log in.")
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        # Call Flask's logout API first
        try:
            response = requests.post(
                f"{settings.FLASK_API_BASE}/api/logout",
                cookies=request.COOKIES,
                headers={'X-CSRFToken': request.COOKIES.get('csrftoken', '')}
            )
        except Exception as e:
            messages.error(request, f"Error connecting to Flask: {str(e)}")

        # Then perform Django logout
        if request.user.is_authenticated:
            messages.info(request, "Logged out successfully!")
            logout(request)  # This logs out the Django user

        return super().dispatch(request, *args, **kwargs)

    def get_next_page(self):
        return reverse_lazy('job_portal:index')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'jobs/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
              
        # Get recent jobs through the API
        try:
            response = requests.get(f"{FLASK_API_BASE}/jobs")
            context['recent_jobs'] = response.json()[:5] if response.status_code == 200 else []
        except requests.RequestException:
            context['recent_jobs'] = []
            
        return context

class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'jobs/profile.html'
    model = CustomUser
    fields = ['name', 'email', 'mobile']
    success_url = reverse_lazy('job_portal:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

# Admin Mixin
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

    def handle_no_permission(self):
        return HttpResponseForbidden(render(self.request, 'jobs/error.html', {
            'error_code': 403,
            'error_message': 'Access Forbidden',
            'error_description': 'You do not have permission to access this resource.'
        }))

class PostJobView(AdminRequiredMixin, FormView):
    template_name = 'jobs/post_job.html'
    form_class = JobPostForm
    success_url = reverse_lazy('job_portal:index')

    def form_valid(self, form):
        data = form.cleaned_data
        payload = {
            "title": data['title'],
            "company_id": data['company'],  # Use the selected company ID
            "description": data['description'],
            "location": data.get('location', ''),
            "salary_range": data.get('salary_range', ''),
            "job_type": data.get('job_type', ''),
            "requirements": data.get('requirements', '')
        }
        
        try:
            response = requests.post(
                f"{settings.FLASK_API_BASE}/job",
                json=payload,
                headers={'Content-Type': 'application/json'},
                cookies=self.request.COOKIES
            )
            
            if response.status_code == 201:
                messages.success(self.request, "Job posted successfully!")
                return super().form_valid(form)
            else:
                messages.error(self.request, f"Error posting job: {response.json().get('error', 'Unknown error')}")
                return self.form_invalid(form)
                
        except requests.RequestException as e:
            messages.error(self.request, f"Error connecting to API: {str(e)}")
            return self.form_invalid(form)

class UpdateJobView(AdminRequiredMixin, View):
    def get(self, request, pk):
        try:
            response = requests.get(f"{FLASK_API_BASE}/job/{pk}")
            job_data = response.json() if response.status_code == 200 else None
            
            if not job_data:
                return render(request, 'jobs/error.html', {
                    'error_code': 404,
                    'error_message': 'Job Not Found',
                }, status=404)
                
            form = JobPostForm(initial={
                'title': job_data['title'],
                'company': job_data['company_id'],
                'description': job_data['description'],
                'location': job_data['location'],
                'salary_range': job_data['salary_range'],
                'job_type': job_data['job_type'],
                'requirements': job_data['requirements'],
            })
            
            return render(request, 'jobs/update_job.html', {
                'form': form,
                'job_id': pk,  # Ensure this is passed as job_id
                'job': job_data  # Optional: pass full job data if needed
            })
            
        except requests.RequestException as e:
            messages.error(request, f"Error connecting to API: {str(e)}")
            return redirect('job_portal:dashboard')
        
class DeleteJobView(AdminRequiredMixin, View):
    def post(self, request, pk):
        try:
            response = requests.delete(
                f"{FLASK_API_BASE}/job/{pk}",
                cookies=request.COOKIES
            )
            
            if response.status_code == 200:
                messages.success(request, "Job deleted successfully!")
            else:
                messages.error(request, f"Error deleting job: {response.json().get('error', 'Unknown error')}")
        except requests.RequestException as e:
            messages.error(request, f"Error connecting to API: {str(e)}")
            
        return redirect('job_portal:index')

class CompanyListView(AdminRequiredMixin, View):
    model = Company
    def get(self, request):
        try:
            response = requests.get(f"{FLASK_API_BASE}/companies")
            companies = response.json() if response.status_code == 200 else []
        except requests.RequestException as e:
            companies = []
            messages.error(request, f"Error connecting to API: {str(e)}")
            
        return render(request, 'jobs/companies.html', {'companies': companies})

class AddCompanyView(AdminRequiredMixin, FormView):
    form_class = CompanyForm
    template_name = 'jobs/add_company.html'
    success_url = reverse_lazy('job_portal:list_companies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['FLASK_API_BASE'] = settings.FLASK_API_BASE
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        payload = {
            "name": data['name'],
            "description": data.get('description', ''),
            "logo_url": data.get('logo_url', '') or None  # Send None if empty
        }
        
        try:
            # Include CSRF token in headers for Flask if needed
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.request.COOKIES.get('csrftoken', '')
            }
            
            response = requests.post(
                f"{settings.FLASK_API_BASE}/company",
                json=payload,
                headers=headers,
                cookies=self.request.COOKIES
            )
            
            if response.status_code == 201:
                messages.success(self.request, "Company added successfully!")
                return super().form_valid(form)
            else:
                error_msg = response.json().get('error', 'Unknown error')
                messages.error(self.request, f"Error adding company: {error_msg}")
                return self.form_invalid(form)
                
        except requests.RequestException as e:
            messages.error(self.request, f"API connection error: {str(e)}")
            return self.form_invalid(form)
        except json.JSONDecodeError:
            messages.error(self.request, "Invalid response from server")
            return self.form_invalid(form)