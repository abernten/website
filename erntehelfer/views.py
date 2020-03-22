from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import Group

from .models import CompanyProfile, CitizenProfile, LicenseClass, User
from .forms import RegisterCitizenForm, RegisterCompanyForm
from interests.models import InterestOffer
from tasks.models import Task, Category

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
        form = RegisterCitizenForm(request.POST)

        if form.is_valid():
            if form.cleaned_data['password'] != form.cleaned_data['password_2']:
                messages.error(request, 'Passwörter stimmen nicht überein!', extra_tags='alert-danger')
                return render(request, 'registration/register-citizen.html')

            group = Group.objects.get(name='Helfer')

            user = User()
            user.username = form.cleaned_data['username']
            user.email    = form.cleaned_data['email']
            user.password = form.cleaned_data['password']
            user.save()

            user.groups.add(group)

            citizen = CitizenProfile()
            citizen.owner = user
            citizen.date_of_birth = form.cleaned_data['date_of_birth']
            citizen.save()

            login(request, user)

            messages.success(request, 'Benutzerkonto wurde erfolgreich erstellt!', extra_tags='alert-success')
            return redirect('/dashboard')
        else:
            messages.error(request, 'Ein Fehler ist aufgetreten. Bitte überprüfe deine Eingaben!', extra_tags='alert-danger')
            return render(request, 'registration/register-citizen.html', {
                'form': form
            })

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

class SettingsView(View):

    def get(self, request):
        if request.user.groups.filter(name__in=['Helfer']).exists():
            citizen = CitizenProfile.objects.get(owner__id=request.user.id)
            licenses = LicenseClass.objects.all()
            return render(request, 'settings/citizen.html', {
                'citizen': citizen,
                'licenses': licenses
            })
        else:
            return render(request, 'settings/company.html')

class SettingsUserView(View):

    def get(self, request):
        return render(request, 'settings/user.html')

class DashboardView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def get(self, request):
        if request.user.groups.filter(name__in=['Helfer']).exists():
            citizen = CitizenProfile.objects.get(owner__id=request.user.id)
            interests = InterestOffer.objects.filter(citizen__id=citizen.id, task__done=False).order_by('-changed_at')
            approved_interests = InterestOffer.objects.filter(citizen__id=citizen.id, task__done=False, state=1)
            # Citizen
            return render(request, 'dashboard/citizen.html', {
                # 'citizen': citizen,
                'interests': interests,
                'approved_interests': approved_interests
            })
        else:
            company = CompanyProfile.objects.get(owner__id=request.user.id)
            tasks = Task.objects.filter(company__id=company.id, done=False)
            interests = InterestOffer.objects.filter(task__company__id=company.id, task__done=False)

            # Company
            return render(request,'dashboard/company.html', {
                'tasks': tasks,
                'interests': interests
            })
