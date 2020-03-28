from django.urls import path, re_path, include
from django.views.generic import TemplateView

from django.contrib.auth import views as auth_views

from .views import *

urlpatterns = [
    # Static pages
    path('', TemplateView.as_view(template_name='index.html')),
    path('imprint', TemplateView.as_view(template_name='imprint.html')),
    path('privacy', TemplateView.as_view(template_name='privacy.html')),

    # Accounts
    # path('accounts/login', LoginView.as_view()),
    # path('accounts/logout', LogoutView.as_view()),
    path('accounts/register', RegisterCompanyView.as_view()),
    path('accounts/', include('django.contrib.auth.urls')),

    # Companies
    path('companies', CompanyListView.as_view()),
    path('companies/<int:id>', CompanyProfileView.as_view()),

    # Settings
    path('settings', SettingsView.as_view()),
    path('settings/user', SettingsUserView.as_view()),
    path('settings/user/delete',DeleteUserView.as_view()),

    # Tasks
    re_path(r'^tasks/?', include('tasks.urls')),
]
