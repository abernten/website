from django.views import View
from django.views.generic import CreateView, UpdateView
from django import forms
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .nominatim import find_coordinates

from .models import Category, Task, TaskOffer
from erntehelfer.models import LicenseClass, CompanyProfile, CitizenProfile
from interests.models import InterestOffer

from .forms import TaskForm, ApplyForm

class TaskListView(View):
    """
    Zeigt eine Liste mit allen offenen Angeboten an
    """

    def get(self, request):
        # Query
        q = Task.objects.filter(done=False)

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
            'licenses': LicenseClass.objects.all(),
            'radius': r
        })

class TaskView(View):
    """
    Zeigt ein bestimmtes Angebot an
    """

    def get(self, request, id):
        task = Task.objects.get(pk=id)
        licenses = task.drivers_licenses.all()
        categories = Category.objects.all()

        # Is requesting user owner of this task?
        is_owner = False
        if request.user.is_authenticated and not request.user.is_helfer():
            is_owner = task.company.owner.id == request.user.id

        # Is requesting user participating in this task?
        is_participating = False
        if request.user.is_authenticated and request.user.is_helfer():
            is_participating = InterestOffer.objects.filter(task__id=task.id, citizen__owner__id=request.user.id).exists()

        return render(request, 'tasks/task.html', {
            'task': task,
            'licenses': licenses,
            'categories': Category.objects.all(),

            'is_owner': is_owner,
            'is_participating': is_participating
        })

class CreateTaskView(CreateView):
    model = Task
    template_name = 'tasks/create.html'
    form_class = TaskForm

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Company profile vor dem Speichern hinzufügen
        self.object.company = CompanyProfile.objects.get(owner__id=self.request.user.id)

        # Koordinaten berechnen und speichern
        if not self.object.find_coordinates():
            # TODO: Message ausgeben
            return self.form_invalid(form)

        return super(CreateTaskView, self).form_valid(form)

class EditTaskView(UpdateView):
    model = Task
    template_name = 'tasks/edit.html'
    form_class = TaskForm

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Koordinaten berechnen und speichern
        if not self.object.find_coordinates():
            # TODO: Message ausgeben
            return self.form_invalid(form)

        return super(EditTaskView, self).form_valid(form)

class FinishTaskView(View):

    def get(self, request, id):
        task = Task.objects.get(pk=id)
        task.done = True
        task.save()
        messages.success(request, 'Die Aufgabe wurde erfolgreich beendet!', extra_tags='alert-success')
        return redirect('/')

class ParticipateTaskView(View):

    def get(self, request, id):
        # Nur Helfer dürfen mitmachen
        if not request.user.is_helfer():
            return redirect('/')

        task = Task.objects.get(pk=id)

        # Fehlermeldung anzeigen wenn bereits mitgemacht wird
        is_participating = False
        if request.user.is_helfer():
            is_participating = InterestOffer.objects.filter(task__id=id, citizen__owner__id=request.user.id).exists()
            if is_participating:
                messages.error(request, 'Du hast bereits das Angebot markiert! Bitte warte auf eine Antwort vom Betrieb.', extra_tags='alert-danger')
                return redirect(task.get_absolute_url())

        interested = InterestOffer()
        interested.task = task
        interested.citizen = CitizenProfile.objects.get(owner__id=request.user.id)
        interested.save()

        messages.success(request, 'Die Aufgabe wurde erfolgreich markiert!',extra_tags='alert-success')
        return redirect(task.get_absolute_url())

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
