from django.forms import ModelForm
from django import forms

from .models import Task, TaskOffer

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'helpers_count',
            'start_date',
            'end_date',
            'category',
            'drivers_licenses',
            'zip_code'
        ]
        widgets = {
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'end_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})
        }

class ApplyForm(ModelForm):
    class Meta:
        model = TaskOffer
        fields = [
            'full_name',
            'date_of_birth',
            'email',
            'phone',
            'drivers_licenses',
            'message'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }
