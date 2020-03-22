from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=250, blank=True, null=True)

class Category(models.Model):
    class Meta:
        verbose_name        = 'Kategorie'
        verbose_name_plural = 'Kategorien'

    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Task(models.Model):
    class Meta:
        verbose_name        = 'Aufgabe'
        verbose_name_plural = verbose_name + 'n'

    # Besitzer
    company = models.ForeignKey('CompanyProfile', on_delete=models.CASCADE)

    # Grunddaten
    title       = models.CharField(max_length=250)
    description = models.TextField() # Art des Jobs
    category    = models.ForeignKey('Category', on_delete=models.PROTECT)
    zip_code    = models.CharField(max_length=16, blank=True, null=True)

    # Beginn und Ende
    start_date = models.DateField()
    end_date   = models.DateField()

    # Erforderliche Führerscheinklassen
    drivers_licenses = models.ManyToManyField('LicenseClass', blank=True) # Liste an Fueherscheinen

    # Kennzeichen, wenn die Aufgabe eingestellt wurde
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title

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

class InterestOffer(models.Model):
    class Meta:
        verbose_name        = "Interessensangebot"
        verbose_name_plural = verbose_name + 'e'

    STATES = [
        (0, 'Offen'),
        (1, 'Bestätigt'),
        (2, 'Abgelehnt'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    # Status
    state = models.IntegerField(default=0, choices=STATES)

    # Referenzen
    task    = models.ForeignKey('Task', on_delete=models.CASCADE)
    citizen = models.ForeignKey('CitizenProfile', on_delete=models.CASCADE)

    def __str__(self):
        return 'Angebot von "{} {}" an "{}"'.format(self.citizen.owner.first_name, self.citizen.owner.last_name, self.task.title)

