from django import forms
from django.forms import ModelForm, Form

from .models import User, CompanyProfile

class RegisterCompanyForm(Form):
    username = forms.CharField(label='Benutzername', max_length=150)

    company_name = forms.CharField(label='Betriebsname', max_length=250)
    company_number = forms.CharField(label='Betriebsnummer (optional)',max_length=250, required=False)

    email = forms.EmailField(label='E-Mail Adresse', max_length=150)
    phone = forms.CharField(label='Telefonnummer',max_length=150, required=True)

    password = forms.CharField(label='Passwort', max_length=100, widget=forms.PasswordInput)
    password_2 = forms.CharField(label='Passwort bestätigen', max_length=100, widget=forms.PasswordInput)

class SettingsCompanyForm(ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'company_name',
            'company_number',
            'street',
            'zip_code',
            'city',
            'description'
        ]

class SettingsUserForm(ModelForm):
    email = forms.EmailField(max_length=150, label='E-Mail Adresse')
    phone = forms.CharField(max_length=150, label='Telefonnummer')

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone'
        ]
