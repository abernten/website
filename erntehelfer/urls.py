from django.urls import path
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    # Static pages
    path('', IndexView.as_view()),
    path('imprint', TemplateView.as_view(template_name='imprint.html')),
    path('privacy', TemplateView.as_view(template_name='privacy.html')),

    # Accounts
    path('accounts/login', LoginView.as_view()),
    path('accounts/logout', LogoutView.as_view()),
    path('accounts/register-citizen', RegisterCitizenView.as_view()),
    path('accounts/register-company', RegisterCompanyView.as_view()),

    # Companies
    path('companies', CompanyListView.as_view()),
    path('companies/<int:id>', CompanyProfileView.as_view()),

    # Settings
    path('settings', SettingsView.as_view()),
    path('settings/user', SettingsUserView.as_view()),

    # Tasks
    path('tasks', TaskListView.as_view()),
    path('tasks/edit/<int:id>', EditTaskView.as_view()),
    path('tasks/create', CreateTaskView.as_view()),
    path('tasks/<int:id>', TaskView.as_view()),

    # Dashboard
    path('dashboard', DashboardView.as_view()),

    # Interested
    path('interests', InterestOfferView.as_view())
]

