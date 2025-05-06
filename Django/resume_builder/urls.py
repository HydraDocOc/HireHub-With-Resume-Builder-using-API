from django.urls import path,include
from . import views

app_name = 'resume_builder'

urlpatterns = [
    path('/', include(('job_portal.urls', 'job_portal'), namespace='job_portal')),
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_resume, name='create_resume'),
    path('<int:pk>/edit/', views.edit_resume, name='edit_resume'),
    path('<int:pk>/personal-info/', views.edit_personal_info, name='edit_personal_info'),
    path('<int:pk>/education/', views.edit_education, name='edit_education'),
    path('<int:pk>/experience/', views.edit_experience, name='edit_experience'),
    path('<int:pk>/skills/', views.edit_skills, name='edit_skills'),
    path('<int:pk>/projects/', views.edit_projects, name='edit_projects'),
    path('<int:pk>/certificates/', views.edit_certificates, name='edit_certificates'),
    path('<int:pk>/languages/', views.edit_languages, name='edit_languages'),
    path('<int:pk>/preview/', views.preview_resume, name='preview_resume'),
    path('<int:pk>/download/', views.download_resume, name='download_resume'),
    path('<int:pk>/delete/', views.delete_resume, name='delete_resume'),
]
