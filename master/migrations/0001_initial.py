# Generated by Django 3.2.20 on 2023-09-09 19:09

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Kecamatan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'db_table': 'kecamatans',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nodes', models.CharField(max_length=200, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('location', models.TextField()),
                ('latitude', models.CharField(max_length=255)),
                ('longitude', models.CharField(max_length=255)),
                ('volume', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'db_table': 'places',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='SettingWork',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('minutes', models.IntegerField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'db_table': 'setting_works',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TruckClass',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('classes', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'db_table': 'truck_classes',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TruckType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('truck_type', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'db_table': 'truck_types',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='TypeTime',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('loading_time', models.IntegerField()),
                ('unloading_time', models.IntegerField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
                ('type', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='master.trucktype')),
            ],
            options={
                'db_table': 'type_times',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('no_pol', models.CharField(max_length=255)),
                ('year', models.CharField(max_length=255)),
                ('capacity', models.DecimalField(decimal_places=2, max_digits=12)),
                ('consumption', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
                ('kecamatan', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='kecamatan', to='master.kecamatan')),
                ('truck_class', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='truck_class', to='master.truckclass')),
                ('type', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='type', to='master.trucktype')),
            ],
            options={
                'db_table': 'trucks',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='PlaceDistance',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('distance', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('created_by', models.CharField(blank=True, max_length=200)),
                ('modified_at', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=200)),
                ('from_place', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='from_place', to='master.place')),
                ('to_place', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='to_place', to='master.place')),
            ],
            options={
                'db_table': 'place_distances',
                'ordering': ['-id'],
            },
        ),
    ]
