from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import CompanyProfile, Category, CitizenProfile, Task, LicenseClass
from .forms import TaskForm

class IndexView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/dashboard')
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
                return redirect('/dashboard')
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
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'registration/register-citizen.html')

    def post(self, request):
        pass


class RegisterCompanyView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'registration/register-company.html')

    def post(self, request):
        pass

class CompanyListView(View):

    def get(self, request):
        categories = Category.objects.all()
        companies = CompanyProfile.objects.all()

        return render(request, 'company/list.html', {
            'categories': categories,
            'companies': companies
        })

class CompanyProfileView(View):

    def get(self, request, id):
        company = CompanyProfile.objects.get(pk=id)

        return render(request, 'company/profile.html', {
            'company': company
        })

class SettingsCitizenView(View):

    def get(self, request):
        if request.user.groups.filter(name__in=['Helfer']).exists():
            citizen = CitizenProfile.objects.get(owner__id=request.user.id)
            licenses = LicenseClass.objects.all()
            return render(request, 'settings/citizen.html', {
                'citizen': citizen,
                'licenses': licenses
            })
        else:
            return redirect('/dashboard')

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
        licenses = task.drivers_licenses.all()
        categories = Category.objects.all()
        companies = CompanyProfile.objects.all()

        return render(request, 'tasks/task.html', {
            'categories': categories,
            'companies': companies,
            'task': task,
            'licenses': licenses
        })

class DashboardView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def get(self, request):
        company = CompanyProfile.objects.get(owner__id=request.user.id)
        tasks = Task.objects.filter(company__id=company.id)

        if request.user.groups.filter(name__in=['Helfer']).exists():
            # Citizen
            return render(request, 'dashboard/citizen.html', {
                'tasks': tasks
            })
        else:
            # Company
            return render(request,'dashboard/company.html', {
                'tasks': tasks
            })

class CreateTaskView(View):
    def get(self, request):
        licenses = LicenseClass.objects.all()
        categories = Category.objects.all()

        if request.user.groups.filter(name__in=['Betrieb']).exists():
            return render(request, 'tasks/create.html', {
            'categories': categories,
            'licenses': licenses
            })
        else:
            return redirect('/dashboard')

    def post(self, request):
        company = CompanyProfile.objects.get(owner__id=request.user.id)
        form = TaskForm(request.POST, initial={
            'company': company
        })

        if form.is_valid():
            task = form.save()
            return redirect('/tasks/' + task.id)
        else:
            messages.error(request, 'Bitte überprüfen Sie noch einmal die Eingabe!')
            return render(request, 'tasks/create.html')
