# Generated by Django 3.2.6 on 2021-08-26 01:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_auto_20210822_1157'),
        ('patient', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patients',
            name='room',
        ),
        migrations.CreateModel(
            name='Patients_Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facility', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='organization.facility')),
                ('patient', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='patient.patients')),
                ('room', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='organization.facility_rooms')),
            ],
        ),
    ]
