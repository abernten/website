from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, UpdateView, FormView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.views.generic import CreateView

from .models import CompanyProfile, LicenseClass, User
from .forms import RegisterCompanyForm, SettingsUserForm, SettingsCompanyForm
from tasks.models import Task, Category
from tasks.nominatim import find_coordinates

# Registration for
class RegisterCompanyView(FormView):
    form_class = RegisterCompanyForm
    template_name = 'registration/register-company.html'
    success_url = '/settings'

    def form_valid(self, form):
        # Passwörter prüfen
        if form.cleaned_data['password'] != form.cleaned_data['password_2']:
            messages.error(self.request, 'Die Passwörter simmen nicht überein!', extra_tags='alert-danger')
            return super().form_invalid(form)

        # Prüfen, ob es einen Benutzer mit dem Namen bereits gibt
        if User.objects.filter(username=form.cleaned_data['username']).exists():
            messages.error(self.request, 'Es existiert bereits ein Benutzer mit diesem Benutzernamen!', extra_tags='alert-danger')
            return super().form_invalid(form)

        # Benutzer anlegen
        user = User()
        user.username = form.cleaned_data['username']
        user.password = form.cleaned_data['password']
        user.email = form.cleaned_data['email']
        user.phone = form.cleaned_data['phone']
        user.save()

        # Betriebsprofil anlegen
        company = CompanyProfile()
        company.owner = user
        company.company_name = form.cleaned_data['company_name']
        company.company_number = form.cleaned_data['company_number']
        company.save()

        # Session einloggen
        login(self.request, user)

        # Nachricht ausgeben
        messages.success(self.request, 'Konto wurde erfolgreich erstellt!', extra_tags='alert-success')

        send_mail('Bestätigung Ihrer Registrierung für Abernten.de ',
                      'Hallo Nutzer. \n \n' +
                      'Vielen Dank, dass du Abernten.de nutzt! \n \n' +
                      #</br>
                      'Du kannst Abernten.de nun nutzen. Teile der Community mit, in welchen Bereichen du Hilfe brauchst & überprüfe regelmäßig, ob du Bewerber hast. \n \n'
                      #</br>
                      'Vielen Dank und Frohes Schaffen! \n \n'
                      #</br>
                      'Dein Abernten-Team \n',
                      'info@abernten.de',
                      [company.owner.email])

        return super().form_valid(form)

# Displays all registered companies
class CompanyListView(LoginRequiredMixin,View):

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

# Displays the profile of a company
class CompanyProfileView(LoginRequiredMixin,View):

    def get(self, request, id):
        company = CompanyProfile.objects.get(pk=id)

        return render(request, 'company/profile.html', {
            'company': company
        })

# Displays the company settings
class SettingsView(LoginRequiredMixin,UpdateView):
    model = CompanyProfile
    form_class = SettingsCompanyForm
    template_name = 'settings/company.html'

    def get_success_url(self):
        return '/settings'

    def get_object(self):
        return get_object_or_404(CompanyProfile, owner=self.request.user)

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Koordinaten finden
        if not self.object.find_coordinates():
            messages.error(self.request, 'Ungültige Anschrift. Bitte überprüfe nochmal deine Angaben!', extra_tags='alert-danger')
            return self.form_invalid(form)

        messages.error(self.request, 'Die Einstellungen wurden erfolgreich gespeichert!', extra_tags='alert-success')
        return super(SettingsView, self).form_valid(form)

# Updates the user settings
class SettingsUserView(LoginRequiredMixin,UpdateView):
    model = User
    form_class = SettingsUserForm
    template_name = 'settings/user.html'

    def get_success_url(self):
        return '/settings/user'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Die Einstellungen wurden erfolgreich gespeichert!', extra_tags='alert-success')
        return super().form_valid(form)

# Deletes the user
class DeleteUserView(LoginRequiredMixin,View):

    def get(self, request):
        company = CompanyProfile.objects.get(owner__id=request.user.id)
        user = request.user
        logout(request)

        send_mail('Ihr Account bei Abernten.de wurde gelöscht',
                      'Hallo Nutzer. \n \n' +
                      'Vielen Dank, dass du Abernten.de genutzt hast! \n \n' +
                      #</br>
                      'Wir haben wunschgemäß deinen Account und alle damit verbundenen Informationen gelöscht. \n \n'
                      #</br>
                      'Vielen Dank, \n \n'
                      #</br>
                      'Dein Abernten-Team \n',
                      'info@abernten.de',
                      [company.owner.email])

        company.delete()
        user.delete()



        return redirect('/')

