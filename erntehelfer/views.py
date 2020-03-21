from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import CompanyProfile, Category, CompanyProfile, Task, LicenseClass

# Create your views here.
def index(request):
    return render(request, 'index.html')

class LoginView(View):
    """
    Loggt den Benutzer nach erfolgreicher Eingabe des Benutzernamens
    und des Passworts ein.
    """

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'registration/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Benutzer wurde deaktiviert')
                return render(request, 'registration/login.html')
        else:
            messages.error(request, 'Falscher Benutzername oder falsches Passwort!')
            return render(request, 'registration/login.html')

class LogoutView(View):
    """
    Loggt einen eingeloggten Benutzer aus.
    """

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('/')

class RegisterCitizenView(View):

    def get(self, request):
        return render(request, 'registration/register-citizen.html')

    def post(self, request):
        pass


class RegisterCompanyView(View):

    def get(self, request):
        return render(request, 'registration/register-company.html')

    def post(self, request):
        pass

class CompanyListView(View):

    def get(self, request):
        categories = Category.objects.all()
        companies = CompanyProfile.objects.all()

        return render(request, 'company-list.html', {
            'categories': categories,
            'companies': companies
        })

class CompanyProfileView(View):

    def get(self, request):
        return render(request, 'company-profile.html')

class SettingsCitizenView(View):

    def get(self, request):
        return render(request, 'settings/citizen.html')

class SettingsCompanyView(View):

    def get(self, request):
        return render(request, 'settings/company.html')

class SettingsUserView(View):

    def get(self, request):
        return render(request, 'settings/user.html')

class TaskListView(View):
    def get(self, request):
        categories = Category.objects.all()
        tasks = Task.objects.all()
        licenses = LicenseClass.objects.all()

        return render(request, 'tasks/list.html', {
            'categories': categories,
            'tasks': tasks,
            'licenses': licenses
        })

class TaskView(View):

    def get(self, request, id):
        task = Task.objects.get(pk=id)
        categories = Category.objects.all()
        companies = CompanyProfile.objects.all()

        return render(request, 'tasks/task.html', {
            'categories': categories,
            'companies': companies,
            'task': task
        })
