# Generated by Django 3.0.4 on 2020-03-21 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erntehelfer', '0004_auto_20200321_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='done',
            field=models.BooleanField(default=False),
        ),
    ]
