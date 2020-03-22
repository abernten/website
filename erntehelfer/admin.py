from django.contrib import admin

from .models import User, Category, Task, CompanyProfile, CitizenProfile, LicenseClass, InterestOffer

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Task)
admin.site.register(CompanyProfile)
admin.site.register(CitizenProfile)
admin.site.register(LicenseClass)
admin.site.register(InterestOffer)
