from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string

from datetime import datetime

from .nominatim import find_coordinates

from .models import Category, Task, TaskOffer
from erntehelfer.models import CompanyProfile

from .forms import TaskForm, ApplyForm

# Displays all currently active tasks
class TaskListView(View):
    """
    Zeigt eine Liste mit allen offenen Angeboten an
    """

    def get(self, request):
        # Query
        q = Task.objects.filter(done=False, end_date__gt=datetime.now())

        # Search parameter
        cat = request.GET.get('cat')
        if cat and not cat == '0':
            q = q.filter(category__id=cat)

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
            filtered_tasks = [task.id for task in q if task.in_radius(cords, r)]
            q = q.filter(id__in=filtered_tasks)

        # Order by start_date
        q = q.order_by('start_date')

        # Task paginator
        paginator = Paginator(q, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'tasks/list.html', {
            'task_count': paginator.count,
            'num_pages': paginator.num_pages,
            'page_obj': page_obj,
            'categories': Category.objects.all(),
            'radius': r
        })

# Displays the details of a certain task
class TaskView(TemplateView):
    """
    Zeigt ein bestimmtes Angebot an
    """

    template_name = 'tasks/task.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Instanz vom Inserat
        task = get_object_or_404(Task, pk=kwargs['id'])
        context['task'] = task

        # Alle Kategorien
        context['categories'] = Category.objects.all()

        # Ist der eingeloggte Benutzer Besitzer des Inserats?
        context['is_owner'] = (
            self.request.user.is_authenticated and
            task.company.owner.id == self.request.user.id)

        return context

# Creates a new task in the DB
class CreateTaskView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Task
    template_name = 'tasks/create.html'
    form_class = TaskForm
    login_url = '/accounts/login'

    def test_func(self):
        company = get_object_or_404(CompanyProfile, owner=self.request.user)
        return company.street and company.zip_code and company.city

    def handle_no_permission(self):
        messages.error(self.request, 'Bitte vervollständige die Anschrift in deinem Firmenprofil bevor du Inserate anlegst!', extra_tags='alert-danger')
        return redirect('/settings')

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Prüfen, ob Startzeitpunkt
        if self.object.start_date > self.object.end_date:
            messages.error(self.request, 'Ungültiges Enddatum', extra_tags='alert-danger')
            return self.form_invalid(form)

        # Company profile vor dem Speichern hinzufügen
        self.object.company = get_object_or_404(CompanyProfile, owner=self.request.user)

        # Koordinaten berechnen und speichern
        if not self.object.find_coordinates():
            messages.success(self.request, 'Inserat wurde erfolgreich erstellt!', extra_tags='alert-success')
            return self.form_invalid(form)

        return super(CreateTaskView, self).form_valid(form)

# Changes parameters of a certain task
class EditTaskView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = 'tasks/edit.html'
    form_class = TaskForm
    login_url = '/accounts/login'

    def test_func(self):
        return self.request.user == self.get_object().company.owner

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Koordinaten berechnen und speichern
        if not self.object.find_coordinates():
            messages.error(self.request, 'Ungültige Postleitzahl!', extra_tags='alert-danger')
            return self.form_invalid(form)

        messages.success(self.request, 'Inserat wurde erfolgreich bearbeitet!', extra_tags='alert-success')
        return super(EditTaskView, self).form_valid(form)

# sets the task to done
class FinishTaskView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/accounts/login'

    def test_func(self):
        return self.request.user == get_object_or_404(Task, pk=id).owner

    def get(self, request, id):
        task = get_object_or_404(Task, pk=id)

        if not task.done:
            task.done = True
            task.save()

        return redirect(task.get_absolute_url())

# extends the apply form
class ApplyTaskView(CreateView):
    model = TaskOffer
    template_name = 'tasks/apply.html'
    form_class = ApplyForm

    def form_valid(self, form):
        self.object = form.save(commit=False)

        task = get_object_or_404(Task, pk=self.kwargs['id'])
        self.object.task = task

        # E-Mail an Betrieb senden
        tmpl = render_to_string('emails/new-offer.txt', {
            'username': task.company.owner.username,
            'full_name': self.object.full_name,
            'title': task.title
        })
        send_mail('[Abernten.de] Du hast eine neue Bewerbung!', tmpl, 'info@abernten.de', [task.company.owner.email])

        messages.success(self.request, 'Vielen Dank, dass du deine Hilfe anbietest! Du erhälst demnächst eine Antwort vom Betrieb.', extra_tags='alert-success')

        return super(ApplyTaskView, self).form_valid(form)

# Displays a list of my currently active tasks
class MyTaskListView(LoginRequiredMixin, View):

    def get(self, request):
        company = get_object_or_404(CompanyProfile, owner=request.user)

        # Query
        q = company.get_open_tasks().order_by('start_date')

        # Task paginator
        paginator = Paginator(q, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'tasks/my-task-list.html', {
            'task_count': paginator.count,
            'num_pages': paginator.num_pages,
            'page_obj': page_obj
        })

# Displays all unanswered offers
class OpenOffersListView(LoginRequiredMixin, ListView):
    model = TaskOffer
    paginate_by = 5
    template_name = 'taskoffers/open.html'

    def get_queryset(self):
        company = get_object_or_404(CompanyProfile, owner=self.request.user)
        return TaskOffer.objects.filter(task__company=company, state=TaskOffer.OPEN, task__done=False, task__end_date__gt=datetime.now()).order_by('-updated_at')

# Displays all already accepted offers
class AcceptedOffersListView(LoginRequiredMixin, ListView):
    model = TaskOffer
    paginate_by = 20
    template_name = 'taskoffers/accepted.html'

    def get_queryset(self):
        company = get_object_or_404(CompanyProfile, owner=self.request.user)
        return TaskOffer.objects.filter(task__company=company, state=TaskOffer.ACCEPTED, task__done=False, task__end_date__gt=datetime.now()).order_by('-updated_at')

# Displays all declined offers
class DeclinedOffersListView(LoginRequiredMixin, ListView):
    model = TaskOffer
    paginate_by = 20
    template_name = 'taskoffers/declined.html'

    def get_queryset(self):
        company = get_object_or_404(CompanyProfile, owner=self.request.user)
        return TaskOffer.objects.filter(task__company=company, state=TaskOffer.DECLINED, task__done=False, task__end_date__gt=datetime.now()).order_by('-updated_at')

# accepts a taskoffer
class AcceptTaskOfferView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user == get_object_or_404(TaskOffer, pk=self.kwargs['id']).task.company.owner

    def get(self, request, id):
        # Save task offer
        offer = get_object_or_404(TaskOffer, pk=id)
        offer.state = TaskOffer.ACCEPTED
        offer.save()

        company = offer.task.company

        # Mail an Helfer
        tmpl = render_to_string('emails/offer-accepted.txt', {
            'full_name': offer.full_name,
            'title': offer.task.title,
            'created_at': offer.created_at,
            'company_name': company.company_name,
            'street': company.street,
            'zip_code': company.zip_code,
            'city': company.city,
            'phone': company.owner.phone,
            'email':company.owner.email
        })
        send_mail('[Abernten.de] Deine Bewerbung bei {} wurde akzeptiert!'.format(company.company_name), tmpl, 'info@abernten.de', [offer.email])

        # Mail an Betrieb
        tmpl = render_to_string('emails/offer-accepted-company.txt', {
            'username': request.user.username,
            'title': offer.task.title,
            'full_name': offer.full_name,
            'phone': offer.phone,
            'email': offer.email
        })
        send_mail('[Abernten.de] Du hast die Bewerbung von einem Helfer akzeptiert', tmpl, 'info@abernten.de', [company.owner.email])

        messages.success(request, 'Die Kontaktdaten werden an den Interessenten versendet!',extra_tags='alert-success')
        return redirect('/tasks/offers/accepted')

# Declines a canditature and deletes the database entry
class DeclineTaskOfferView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user == get_object_or_404(TaskOffer, pk=self.kwargs['id']).task.company.owner

    def get(self, request, id):
        # Company
        offer = get_object_or_404(TaskOffer, pk=id)
        offer.state = TaskOffer.DECLINED
        offer.save()

        company = offer.task.company

        # Mail an Helfer
        tmpl = render_to_string('emails/offer-declined.txt', {
            'full_name': offer.full_name,
            'created_at': offer.created_at,
            'title': offer.task.title
        })

        send_mail('[Abernten.de] Deine Bewerbung bei {} wurde abgelehnt!'.format(company.company_name), tmpl, 'info@abernten.de', [offer.email])

        # offer.delete()

        messages.success(request, 'Der Helfer wurde über die Ablehnung informiert!',extra_tags='alert-success')
        return redirect('/tasks/offers/declined')
