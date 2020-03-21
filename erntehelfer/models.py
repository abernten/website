from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    street_1 = models.CharField(max_length=250)
    street_2 = models.CharField(max_length=250, blank=True, null=True)
    zip_code = models.CharField(max_length=16)
    city     = models.CharField(max_length=250)
    country  = models.CharField(max_length=2) # Zweistelliger Laendercode
    phone    = models.CharField(max_length=250, blank=True, null=True)

class Category(models.Model):
    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorien'

    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Task(models.Model):
    class Meta:
        verbose_name = 'Aufgabe'
        verbose_name_plural = verbose_name + 'n'

    title        = models.CharField(max_length=250)
    start_date   = models.DateField()
    end_date     = models.DateField()
    description  = models.TextField() # Art des Jobs
    company      = models.ForeignKey('CompanyProfile', on_delete=models.CASCADE)
    category     = models.ForeignKey('Category', on_delete=models.PROTECT)
    interested   = models.ManyToManyField('CitizenProfile', blank=True)
    drivers_licenses = models.ManyToManyField('LicenseClass', blank=True) # Liste an Fueherscheinen

    def __str__(self):
        return self.title

class CompanyProfile(models.Model):
    class Meta:
        verbose_name = 'Betriebsprofil'
        verbose_name_plural = verbose_name + 'e'

    owner          = models.ForeignKey('User', on_delete=models.CASCADE)
    company_name   = models.CharField(max_length=250)
    description    = models.TextField()
    company_number = models.CharField(max_length=12, blank=True, null=True) # Betriebsnummer != PK, optional

    def __str__(self):
        return self.company_name

class CitizenProfile(models.Model):
    class Meta:
        verbose_name = 'Helferprofil'
        verbose_name_plural = verbose_name + 'e'

    owner            = models.ForeignKey('User', on_delete=models.CASCADE)
    date_of_birth    = models.DateField()
    drivers_licenses = models.ManyToManyField('LicenseClass') # Liste an Fueherscheinen

    def __str__(self):
        return '{} {}'.format(self.owner.firstname, self.owner.lastname)

class LicenseClass(models.Model):
    class Meta:
        verbose_name = 'Führerscheinklasse'
        verbose_name_plural = verbose_name + 'n'

    class_name = models.CharField(max_length=3) # EU-Fuehrerscheinklassen

    def __str__(self):
        return 'Klasse ' + self.class_name
