from django import forms
from django.forms import ModelForm, Form

from .models import User, CitizenProfile

class RegisterCitizenForm(Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)
    date_of_birth = forms.DateField()
    password = forms.CharField(max_length=100)
    password_2 = forms.CharField(max_length=100)

class RegisterCompanyForm(Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)
    password = forms.CharField(max_length=100)
    password_2 = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=250)
    company_number = forms.CharField(max_length=250, required=False)

class SettingsCitizenForm(ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    #phone = forms.CharField(max_length=150, required=False)

    class Meta:
        model = CitizenProfile
        fields = ['drivers_licenses', 'date_of_birth', 'description']
