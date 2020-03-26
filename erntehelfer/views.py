from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import Group

from tasks.nominatim import find_coordinates
from django.core.paginator import Paginator

from .models import CompanyProfile, CitizenProfile, LicenseClass, User
from .forms import RegisterCitizenForm, RegisterCompanyForm, SettingsUserForm, SettingsCitizenForm, SettingsCompanyForm
from interests.models import InterestOffer
from tasks.models import Task, Category

class IndexView(View):

    def get(self, request):
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
            user.phone = form.cleaned_data['phone']
            user.save()

            user.groups.add(group)

            citizen = CitizenProfile()
            citizen.owner = user
            citizen.date_of_birth = form.cleaned_data['date_of_birth']
            citizen.save()

            login(request, user)

            messages.success(request, 'Benutzerkonto wurde erfolgreich erstellt!', extra_tags='alert-success')
            return redirect('/')
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
        form = RegisterCompanyForm(request.POST)

        if form.is_valid():
            if form.cleaned_data['password'] != form.cleaned_data['password_2']:
                messages.error(request, 'Passwörter stimmen nicht überein!', extra_tags='alert-danger')
                return render(request, 'registration/register-company.html')

            group = Group.objects.get(name='Betrieb')

            user = User()
            user.username = form.cleaned_data['username']
            user.email    = form.cleaned_data['email']
            user.password = form.cleaned_data['password']
            user.phone = form.cleaned_data['phone']
            user.save()

            user.groups.add(group)

            company = CompanyProfile()
            company.owner = user
            company.company_name = form.cleaned_data['company_name']
            company.company_number = form.cleaned_data['company_number']
            company.save()

            login(request, user)

            messages.success(request, 'Benutzerkonto wurde erfolgreich erstellt!', extra_tags='alert-success')
            return redirect('/')
        else:
            messages.error(request, 'Ein Fehler ist aufgetreten. Bitte überprüfe deine Eingaben!', extra_tags='alert-danger')
            return render(request, 'registration/register-company.html', {
                'form': form
            })

class CompanyListView(View):

    def get(self, request):
        categories = Category.objects.all()

        # Query
        q = CompanyProfile.objects.all()

        # Radius
        # Hier wäre eventuell GeoDjango sinnvoll (TODO für später)
        r = request.GET.get('r')
        loc = request.GET.get('loc')
        if loc:
            try:
                r = int(r)
            except:
                r = 50
            cords = find_coordinates(loc)
            filtered_companies = [company.id for company in q if company.in_radius(cords, r)]
            q = q.filter(id__in=filtered_companies)



        # Task paginator
        paginator = Paginator(q, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'company/list.html', {
            'q': q,
            'radius': r,
            'company_count': paginator.count,
            'num_pages': paginator.num_pages,
            'page_obj': page_obj
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
            #citizen
            citizen = CitizenProfile.objects.get(owner__id=request.user.id)
            licenses = LicenseClass.objects.all()
            return render(request, 'settings/citizen.html', {
                'citizen': citizen,
                'licenses': licenses
            })
        else:
            #company
            company = CompanyProfile.objects.get(owner__id=request.user.id)
            return render(request, 'settings/company.html',{
                'company': company
            })

    def post(self, request):
        if request.user.groups.filter(name__in=['Helfer']).exists():
            #citizen
            form = SettingsCitizenForm(request.POST)

            citizen = CitizenProfile.objects.get(owner__id=request.user.id)
            licenses = LicenseClass.objects.all()

            if form.is_valid():
                citizen.description = form.cleaned_data['description']
                citizen.drivers_licenses.set(form.cleaned_data['drivers_licenses'])
                citizen.date_of_birth = form.cleaned_data['date_of_birth']
                citizen.save()
            return render(request, 'settings/citizen.html', {
                'citizen': citizen,
                'licenses': licenses
            })
        else:
            #company
            form = SettingsCompanyForm(request.POST)
            company = CompanyProfile.objects.get(owner__id=request.user.id)

            if form.is_valid():
                company.description = form.cleaned_data['description']
                company.street = form.cleaned_data['street']
                company.zip_code = form.cleaned_data['zip_code']
                company.city = form.cleaned_data['city']
                company.country = form.cleaned_data['country']
                company.owner.phone = form.cleaned_data['phone']
                company.company_number = form.cleaned_data['company_number']
                company.company_name = form.cleaned_data['company_name']

                #calculate coordinates
                company.find_coordinates()

                company.save()

            return render(request, 'settings/company.html',{
                'company': company
            })

class SettingsUserView(View):

    def get(self, request):
        user = request.user

        return render(request, 'settings/user.html',{
            'user': user
        })

    def post(self, request):
        user = request.user
        form = SettingsUserForm(request.POST)

        if form.is_valid():
            user.phone = form.cleaned_data['phone']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

        return render(request, 'settings/user.html',{
            'user': user
        })

class ResetPasswordView(View):
    def get(self,request):
        return render(request, 'registration/reset-password.html',{

        })

