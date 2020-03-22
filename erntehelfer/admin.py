from django.contrib import admin

from .models import User, CompanyProfile, CitizenProfile, LicenseClass

# Register your models here.
admin.site.register([
    User,
    CompanyProfile,
    CitizenProfile,
    LicenseClass
])
