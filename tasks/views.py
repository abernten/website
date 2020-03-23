from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Category, Task
from erntehelfer.models import LicenseClass, CompanyProfile, CitizenProfile
from interests.models import InterestOffer

from .forms import TaskForm

class TaskListView(View):
    def get(self, request):
        categories = Category.objects.all()
        tasks = Task.objects.filter(done=False)
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

        is_helfer = request.user.groups.filter(name__in=['Helfer']).exists()
        is_owner = False
        is_participating = False

        if request.user.groups.filter(name__in=['Betrieb']).exists():
            company = CompanyProfile.objects.get(owner__id=request.user.id)
            is_owner = task.company.id == company.id

        if request.user.groups.filter(name__in=['Helfer']).exists():
            is_participating = InterestOffer.objects.filter(task__id=id, citizen__owner__id=request.user.id).exists()

        return render(request, 'tasks/task.html', {
            'categories': categories,
            'companies': companies,
            'task': task,
            'licenses': licenses,
            'is_helfer': is_helfer,
            'is_owner': is_owner,
            'is_participating': is_participating
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
            return redirect('/')

    def post(self, request):
        company = CompanyProfile.objects.get(owner__id=request.user.id)
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.company = company
            task.save()
            return redirect('/tasks/{}'.format(task.id))
        else:
            messages.error(request, 'Bitte überprüfen Sie noch einmal die Eingabe!')
            return render(request, 'tasks/create.html', {'form': form})

class EditTaskView(View):

    def get(self, request, id):
        task = Task.objects.get(pk=id)
        licenses = LicenseClass.objects.all()
        categories = Category.objects.all()

        if request.user.groups.filter(name__in=['Betrieb']).exists():
            return render(request, 'tasks/edit.html', {
                'categories': categories,
                'licenses': licenses,
                'task': task
            })
        else:
            return redirect('/')

    def post(self, request, id):
        if request.user.groups.filter(name__in=['Betrieb']).exists():

            task = Task.objects.get(pk=id)

            form = TaskForm(request.POST, instance=task)

            if form.is_valid():
                form.save()

                # task.title = form.cleaned_data['title']
                # task.category = Category.objects.get(pk=form.cleaned_data['category'])
                # task.drivers_licenses.set(form.cleaned_data['drivers_licenses'])
                # task.start_date = form.cleaned_data['start_date']
                # task.end_date = form.cleaned_data['end_date']
                # task.zip_code = form.cleaned_data['zip_code']
                # task.description = form.cleaned_data['description']
                # task.save()

            return redirect('/tasks/{}'.format(id))
        else:
            return redirect('/')

class FinishTaskView(View):

    def get(self, request, id):
        task = Task.objects.get(pk=id)
        task.done = True
        task.save()
        messages.success(request, 'Die Aufgabe wurde erfolgreich beendet!', extra_tags='alert-success')
        return redirect('/')

class ParticipateTaskView(View):

    def get(self, request, id):
        task = Task.objects.get(pk=id)

        interested = InterestOffer()
        interested.task = task
        interested.citizen = CitizenProfile.objects.get(owner__id=request.user.id)
        interested.save()

        messages.success(request, 'Die Aufgabe wurde erfolgreich markiert!',extra_tags='alert-success')
        return redirect('/')
