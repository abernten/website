from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, CompanyProfile, CitizenProfile, LicenseClass

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register([
    CompanyProfile,
    CitizenProfile,
    LicenseClass
])
