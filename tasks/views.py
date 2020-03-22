from django.shortcuts import render

from .models import Category, Task
from erntehelfer.models import LicenseClass, CompanyProfile, CitizenProfile

from .forms import TaskForm

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

        is_helfer = request.user.groups.filter(name__in=['Helfer']).exists()
        is_owner = False
        if request.user.groups.filter(name__in=['Betrieb']).exists():
            company = CompanyProfile.objects.get(owner__id=request.user.id)
            is_owner = task.company.id == company.id

        return render(request, 'tasks/task.html', {
            'categories': categories,
            'companies': companies,
            'task': task,
            'licenses': licenses,
            'is_helfer': is_helfer,
            'is_owner': is_owner
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
            return redirect('/dashboard')
