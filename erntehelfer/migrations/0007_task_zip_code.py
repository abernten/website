# Generated by Django 3.0.4 on 2020-03-22 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erntehelfer', '0006_auto_20200321_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='zip_code',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]