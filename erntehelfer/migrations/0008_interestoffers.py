# Generated by Django 3.0.4 on 2020-03-22 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('erntehelfer', '0007_task_zip_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterestOffers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('state', models.IntegerField(choices=[(0, 'Offen'), (1, 'Bestätigt'), (2, 'Abgelehnt')], default=0)),
                ('citizen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='erntehelfer.CitizenProfile')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='erntehelfer.Task')),
            ],
            options={
                'verbose_name': 'Interessensangebot',
                'verbose_name_plural': 'Interessensangebote',
            },
        ),
    ]