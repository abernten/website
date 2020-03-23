from django import forms
from django.forms import ModelForm, Form

from .models import User, CitizenProfile, CompanyProfile

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
    class Meta:
        model = CitizenProfile
        fields = ['drivers_licenses', 'date_of_birth', 'description',]

class SettingsCompanyForm(ModelForm):
    phone = forms.CharField(max_length=150, required=True)

    class Meta:
        model = CompanyProfile
        fields = ['company_name','street','zip_code','city','country','company_number','description']

class SettingsUserForm(ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)

    class Meta:
        model = User
        fields = ['phone']
