# Generated by Django 3.2.20 on 2023-09-11 09:11

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('master', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainTrial',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('short_desc', models.TextField(blank=True, null=True)),
                ('velocity', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('loading_armroll', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unloading_armroll', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('loading_dump', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('unloading_dump', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
                ('fuel', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='main_trial', to='master.fuel')),
            ],
            options={
                'db_table': 'main_trials',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TruckHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('truck_id', models.IntegerField()),
                ('reach_minutes', models.DecimalField(decimal_places=2, max_digits=12)),
                ('is_complete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
                ('mtrial', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='truck_history', to='transaction.maintrial')),
                ('type', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='truck_history', to='master.trucktype')),
            ],
            options={
                'db_table': 'truck_history',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TruckDirection',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('takes_time', models.DecimalField(decimal_places=2, max_digits=12)),
                ('amount_km', models.DecimalField(decimal_places=2, max_digits=12)),
                ('emission', models.DecimalField(decimal_places=2, max_digits=12)),
                ('capacity', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
                ('mtrial', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='truck_direction', to='transaction.maintrial')),
                ('place', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='place_truck_direction', to='master.place')),
                ('truck', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='truck_direction', to='transaction.truckhistory')),
            ],
            options={
                'db_table': 'truck_directions',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='PlaceCompletement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=200)),
                ('rest', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
                ('mtrial', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='place_completement', to='transaction.maintrial')),
                ('place', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='place_completement', to='master.place')),
            ],
            options={
                'db_table': 'place_completements',
                'ordering': ['-id'],
            },
        ),
    ]
