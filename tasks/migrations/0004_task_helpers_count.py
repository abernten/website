# Generated by Django 3.0.4 on 2020-03-25 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20200325_1824'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='helpers_count',
            field=models.IntegerField(default=1, verbose_name='Benötigte Helfer'),
        ),
    ]