from django.urls import path
from django.views.generic import TemplateView

from .views import *

# http://localhost:8000/accounts/register-citizen

urlpatterns = [
    path('', index),
    path('accounts/login/', LoginView.as_view()),
    path('accounts/logout/', LogoutView.as_view()),
    path('accounts/register-citizen', RegisterCitizenView.as_view()),
    path('accounts/register-company', RegisterCompanyView.as_view()),
    path('company-list', CompanyListView.as_view()),
    path('company-profile', CompanyProfileView.as_view()),
    path('settings/citizen', SettingsCitizenView.as_view()),
    path('settings/company', SettingsCompanyView.as_view()),
    path('settings/user', SettingsUserView.as_view()),
    path('imprint', TemplateView.as_view(template_name='imprint.html')),
    path('privacy', TemplateView.as_view(template_name='privacy.html')),
    path('tasks', TaskListView.as_view()),
    path('tasks/<int:id>', TaskView.as_view())
]
