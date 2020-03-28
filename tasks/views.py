from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail

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
class CreateTaskView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/create.html'
    form_class = TaskForm
    login_url = '/accounts/login'

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Prüfen, ob Startzeitpunkt
        if self.object.start_date > self.object.end_date:
            messages.error(self.request, 'Ungültiges Enddatum', extra_tags='alert-danger')
            return self.form_invalid(form)

        # Company profile vor dem Speichern hinzufügen
        self.object.company = CompanyProfile.objects.get(owner__id=self.request.user.id)

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
class FinishTaskView(LoginRequiredMixin, View):
    login_url = '/accounts/login'

    def get(self, request, id):
        task = get_object_or_404(Task, pk=id)

        # Nicht der Besitzer des Inserats
        if not request.user.is_authenticated or not task.company.owner.id == request.user.id:
            return redirect('/tasks')

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

        messages.success(self.request, 'Vielen Dank, dass du deine Hilfe anbietest! Du erhälst demnächst eine Antwort vom Betrieb.', extra_tags='alert-success')

        return super(ApplyTaskView, self).form_valid(form)

# Displays a list of my currently active tasks
class MyTaskListView(LoginRequiredMixin,View):

    def get(self, request):
        company = CompanyProfile.objects.get(owner__id=request.user.id)

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

class OpenOffersListView(LoginRequiredMixin,ListView):
    model = TaskOffer
    paginate_by = 5
    template_name = 'taskoffers/open.html'

    def get_queryset(self):
        company = get_object_or_404(CompanyProfile, owner=self.request.user)
        return TaskOffer.objects.filter(task__company=company, state=TaskOffer.OPEN, task__done=False, task__end_date__gt=datetime.now()).order_by('-updated_at')

class AcceptedOffersListView(LoginRequiredMixin,ListView):
    model = TaskOffer
    paginate_by = 20
    template_name = 'taskoffers/accepted.html'

    def get_queryset(self):
        company = get_object_or_404(CompanyProfile, owner=self.request.user)
        return TaskOffer.objects.filter(task__company=company, state=TaskOffer.ACCEPTED, task__done=False, task__end_date__gt=datetime.now()).order_by('-updated_at')

class DeclinedOffersListView(LoginRequiredMixin,ListView):
    model = TaskOffer
    paginate_by = 20
    template_name = 'taskoffers/declined.html'

    def get_queryset(self):
        company = get_object_or_404(CompanyProfile, owner=self.request.user)
        return TaskOffer.objects.filter(task__company=company, state=TaskOffer.DECLINED, task__done=False, task__end_date__gt=datetime.now()).order_by('-updated_at')

class AcceptTaskOfferView(LoginRequiredMixin,View):

    def get(self, request, id):
        # Save task offer
        offer = get_object_or_404(TaskOffer, pk=id)
        offer.state = TaskOffer.ACCEPTED
        offer.save()

        company = offer.task.company

        send_mail('Bestätigung deines Hilfeangebots für ' + offer.task.title,
                    'Hallo ' + offer.full_name + '. \n \n' +
                    'Vielen Dank, dass du Abernten.de nutzt! \n \n' +
                    #</br>
                    'Dein Hilfeangebot vom ' + '{0:%d.%m.%Y}'.format(offer.created_at) + ' wurde akzeptiert. \n \n' +
                    'Hier findest du die Kontaktdaten des Helfers: \n' +
                    'Betriebsname:' + offer.task.company.company_name + ' \n' + offer.task.company.street + '\n'+ offer.task.company.zip_code + ' ' + offer.task.company.city + '\n' + 'Tel: ' + offer.task.company.owner.phone + '\n' + 'Mail: ' + offer.task.company.owner.email + '\n \n' +
                    #</br>
                    'Bitte setze dich mit der Person in Verbindung, um genaueres wie Einsatzzeitraum und Bezahlung zu klären. \n' +
                    #</br>
                    'Vielen Dank und Frohes Schaffen! \n \n'
                    #</br>
                    'Dein Abernten-Team \n',
                    'info@abernten.de',
                    [offer.email]
                )

        send_mail('Bestätigung eines Hilfeangebots für: ' + offer.task.title ,
                    'Hallo ' + company.company_name + '. \n \n' +
                    'Vielen Dank, dass du Abernten.de nutzt! \n \n' +
                    #</br>
                    'Du hast das Hilfeangebot von ' + offer.full_name + ' akzeptiert. \n \n' +
                    'Hier findest du die Kontaktdaten des Helfers: \n' +
                    offer.full_name + ' \n' + 'Tel: ' + offer.phone + '\n' + 'Mail: ' + offer.email + '\n \n' +
                    #</br>
                    'Bitte setze dich mit der Person in Verbindung, um genaueres wie Einsatzzeitraum und Bezahlung zu klären. \n' +
                    #</br>
                    'Vielen Dank und Viele Grüße \n \n'
                    #</br>
                    'Dein Abernten-Team \n',
                    'info@abernten.de',
                    [company.owner.email]
                )

        messages.success(request, 'Die Kontaktdaten werden an den Interessenten versendet!',extra_tags='alert-success')
        return redirect('/tasks/offers/accepted')

# Declines a canditature and deletes the database entry
class DeclineTaskOfferView(LoginRequiredMixin,View):

    def get(self, request, id):
        if request.user.groups.filter(name__in=['Betrieb']).exists():
            # Company
            offer = TaskOffer.objects.get(pk=id)
            offer.state = 2
            offer.save()

            send_mail('Ablehnung ihres Hilfeangebotes für: ' + offer.task.title,
                      'Hallo ' + offer.full_name + '. \n \n' +
                      'Vielen Dank, dass du Abernten.de nutzt! \n \n' +
                      #</br>
                      'Dein Hilfeangebot vom ' + '{0:%d.%m.%Y}'.format(offer.created_at) + ' wurde leider abgelehnt. \n \n' +
                      'Dies kann viele verschiedene Gründe haben. Du kannst dich gerne auf ein anderes Hilfegesuch in deiner Nähe melden. \n \n'
                      #</br>
                      'Vielen Dank und Viele Grüße \n\n'
                      #</br>
                      'Dein Abernten-Team \n',
                      'info@abernten.de',
                      [offer.email]
                    )

            offer.delete()

            messages.success(request, 'Der Helfer wurde über die Ablehnung informiert!',extra_tags='alert-success')
            return redirect('/tasks/offer/declined')
        else:
            return redirect('/')
