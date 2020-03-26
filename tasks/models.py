from django.db import models
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from geopy.distance import geodesic

import requests

class Category(models.Model):
    class Meta:
        verbose_name        = 'Kategorie'
        verbose_name_plural = 'Kategorien'

    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Task(models.Model):
    class Meta:
        verbose_name        = 'Inserat'
        verbose_name_plural = verbose_name + 'e'

    # Besitzer
    company = models.ForeignKey('erntehelfer.CompanyProfile', on_delete=models.CASCADE)

    # Grunddaten
    title         = models.CharField(verbose_name='Kurzbeschreibung', max_length=250)
    description   = models.TextField(verbose_name='Beschreibung des Angebots')
    category      = models.ForeignKey('Category', verbose_name='Kategorie', on_delete=models.PROTECT)
    helpers_count = models.IntegerField(verbose_name='Benötigte Helfer', default=1, validators=[MinValueValidator(1), MaxValueValidator(2000)])

    # Ort
    zip_code  = models.CharField(verbose_name='Postleitzahl', max_length=16)
    longitude = models.DecimalField(max_digits=12, decimal_places=8)
    latitude  = models.DecimalField(max_digits=12, decimal_places=8)

    # Beginn und Ende
    start_date = models.DateField(verbose_name='Beginn')
    end_date   = models.DateField(verbose_name='Ende')

    # Erforderliche Führerscheinklassen
    drivers_licenses = models.ManyToManyField('erntehelfer.LicenseClass', verbose_name='Führerscheinklassen', blank=True) # Liste an Fueherscheinen

    # Kennzeichen, wenn die Aufgabe eingestellt wurde
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/tasks/{}'.format(self.id)

    def find_coordinates(self):
        response = requests.get('https://nominatim.openstreetmap.org/search', params={
            'format': 'json',
            'country': 'germany',
            'postalcode': self.zip_code
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

class TaskOffer(models.Model):
    class Meta:
        verbose_name = 'Bewerbung'
        verbose_name_plural = verbose_name + 'en'

    OPEN     = 0
    ACCEPTED = 1
    DECLINED = 2

    STATE_CHOICES = [
        (OPEN,     'Offen'),
        (ACCEPTED, 'Akzeptiert'),
        (DECLINED, 'Abgelehnt')
    ]

    # Basisdaten
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Verknüpftes Inserat
    task = models.ForeignKey('Task', on_delete=models.PROTECT)

    # Bewerbungsdaten
    full_name        = models.CharField(max_length=250, verbose_name='Vollständiger Name')
    date_of_birth    = models.DateField(verbose_name='Geburtsdatum')
    email            = models.EmailField(verbose_name='E-Mail Adresse')
    phone            = models.CharField(max_length=150, verbose_name='Telefonnummer')
    drivers_licenses = models.ManyToManyField('erntehelfer.LicenseClass', verbose_name='Führerscheinklassen', blank=True)
    message          = models.TextField(verbose_name='Nachricht an den Betrieb')

    # State
    state = models.IntegerField(default=OPEN, choices=STATE_CHOICES)

    def get_absolute_url(self):
        return self.task.get_absolute_url()
