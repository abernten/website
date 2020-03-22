from django.db import models

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
    company = models.ForeignKey('erntehelfer.CompanyProfile', on_delete=models.CASCADE)

    # Grunddaten
    title       = models.CharField(max_length=250)
    description = models.TextField() # Art des Jobs
    category    = models.ForeignKey('Category', on_delete=models.PROTECT)
    zip_code    = models.CharField(max_length=16, blank=True, null=True)

    # Beginn und Ende
    start_date = models.DateField()
    end_date   = models.DateField()

    # Erforderliche Führerscheinklassen
    drivers_licenses = models.ManyToManyField('erntehelfer.LicenseClass', blank=True) # Liste an Fueherscheinen

    # Kennzeichen, wenn die Aufgabe eingestellt wurde
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title
