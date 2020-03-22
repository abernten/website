from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=250, blank=True, null=True)

class CompanyProfile(models.Model):
    class Meta:
        verbose_name        = 'Betriebsprofil'
        verbose_name_plural = verbose_name + 'e'

    # Besitzer
    owner = models.ForeignKey('User', on_delete=models.CASCADE)

    # Grunddaten
    company_name   = models.CharField(max_length=250)
    company_number = models.CharField(max_length=12, blank=True, null=True) # Betriebsnummer != PK, optional

    # Anschrift
    street   = models.CharField(max_length=250, blank=True, null=True)
    zip_code = models.CharField(max_length=16, blank=True, null=True)
    city     = models.CharField(max_length=250, blank=True, null=True)
    country  = models.CharField(max_length=2, blank=True, null=True) # Zweistelliger Laendercode

    # Betriebsbeschreibung
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name

class CitizenProfile(models.Model):
    class Meta:
        verbose_name        = 'Helferprofil'
        verbose_name_plural = verbose_name + 'e'

    # Besitzer
    owner = models.ForeignKey('User', on_delete=models.CASCADE)

    # Grunddaten
    date_of_birth    = models.DateField()
    drivers_licenses = models.ManyToManyField('LicenseClass') # Liste an Fueherscheinen

    # Biografie / Beschreibung
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.owner.first_name, self.owner.last_name)

class LicenseClass(models.Model):
    class Meta:
        verbose_name        = 'Führerscheinklasse'
        verbose_name_plural = verbose_name + 'n'

    # EU-Fuehrerscheinklassen
    class_name = models.CharField(max_length=3)

    def __str__(self):
        return self.class_name
