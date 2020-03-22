from django.forms import ModelForm

from .models import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'start_date', 'end_date', 'description', 'category', 'drivers_licenses', 'zip_code']
