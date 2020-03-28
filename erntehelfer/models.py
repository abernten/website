from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import datetime

import requests

from geopy.distance import geodesic

class User(AbstractUser):
    phone = models.CharField(max_length=250, blank=True, null=True)

    def is_helfer(self):
        return self.groups.filter(name__in=['Helfer']).exists()

class CompanyProfile(models.Model):
    class Meta:
        verbose_name        = 'Betriebsprofil'
        verbose_name_plural = verbose_name + 'e'

    # Besitzer
    owner = models.ForeignKey('User', on_delete=models.CASCADE)

    # Grunddaten
    company_name   = models.CharField(verbose_name='Betriebsname', max_length=250)
    company_number = models.CharField(verbose_name='Betriebsnummer', max_length=12, blank=True, null=True) # Betriebsnummer != PK, optional

    # Anschrift
    street   = models.CharField(verbose_name='Straße und Hausnummer', max_length=250, blank=True, null=True)
    zip_code = models.CharField(verbose_name='Postleitzahl', max_length=16, blank=True, null=True)
    city     = models.CharField(verbose_name='Ort', max_length=250, blank=True, null=True)
    country  = models.CharField(max_length=2, blank=True, null=True) # Zweistelliger Laendercode
    longitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    latitude  = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)

    # Betriebsbeschreibung
    description = models.TextField(verbose_name='Beschreibung über den Betrieb', blank=True, null=True)

    def __str__(self):
        return self.company_name

    def get_open_tasks(self):
        return self.task_set.filter(done=False, end_date__gt=datetime.now())

    def find_coordinates(self):
        response = requests.get('https://nominatim.openstreetmap.org/search', params={
            'format': 'json',
            'q': '{}, {} {}'.format(self.street, self.zip_code, self.city)
        })

        if not response.status_code == requests.codes.ok:
            return False

        places = response.json()
        if len(places) > 0:
            place = places[0]
            self.longitude = place['lon']
            self.latitude = place['lat']
            return True
        return False

    def in_radius(self, cords, radius):
        return geodesic((self.longitude, self.latitude), cords).km < radius

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
