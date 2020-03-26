from django.contrib import admin

from .models import Category, Task, TaskOffer

admin.site.register([
    Category,
    Task,
    TaskOffer
])
