from django.urls import path
from . import views
from . import api_views

app_name = 'job_portal'

urlpatterns = [
    # Job Portal Views
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login',),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('job/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('company/<int:pk>/', views.CompanyProfileView.as_view(), name='company_profile'),
    path('post-job/', views.PostJobView.as_view(), name='post_job'),
    path('update-job/<int:pk>/', views.UpdateJobView.as_view(), name='update_job'),
    path('delete-job/<int:pk>/', views.DeleteJobView.as_view(), name='delete_job'),
    path('search/', views.SearchView.as_view(), name='search_jobs'),
    path('companies/', views.CompanyListView.as_view(), name='list_companies'),
    path('add-company/', views.AddCompanyView.as_view(), name='add_company'),
         
    # Proxy API Endpoints for Flask
    path('api/jobs/', api_views.FlaskJobsAPIView.as_view(), name='api_jobs'),
    path('api/jobs/<int:pk>/', api_views.FlaskJobDetailAPIView.as_view(), name='api_job_detail'),
]
