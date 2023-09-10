from datetime import datetime
from django.db import models

from master.models import *


class MainTrial(models.Model):
    id = models.AutoField(primary_key=True)
    fuel = models.ForeignKey(Fuel, default=None,
                             on_delete=models.CASCADE, related_name='main_trial')

    name = models.CharField(max_length=255)
    short_desc = models.TextField(blank=True, null=True)

    velocity = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)

    loading_armroll = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    unloading_armroll = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)

    loading_dump = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)
    unloading_dump = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "main_trials"
        ordering = ['-id']


class PlaceCompletement(models.Model):
    id = models.AutoField(primary_key=True)
    mtrial = models.ForeignKey(MainTrial, default=None,
                               on_delete=models.CASCADE, related_name='place_completement')
    place = models.ForeignKey(Place, default=None,
                              on_delete=models.CASCADE, related_name='place_completement')
    status = models.CharField(max_length=200)
    rest = models.DecimalField(decimal_places=2, max_digits=12)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "place_completements"
        ordering = ['-id']


class TruckHistory(models.Model):
    id = models.AutoField(primary_key=True)
    mtrial = models.ForeignKey(MainTrial, default=None,
                               on_delete=models.CASCADE, related_name='truck_history')
    type = models.ForeignKey(TruckType, default=None,
                             on_delete=models.CASCADE, related_name='truck_history')
    truck_id = models.IntegerField()

    reach_minutes = models.DecimalField(decimal_places=2, max_digits=12)
    is_complete = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "truck_history"
        ordering = ['-id']


class TruckDirection(models.Model):
    id = models.AutoField(primary_key=True)
    mtrial = models.ForeignKey(MainTrial, default=None,
                               on_delete=models.CASCADE, related_name='truck_direction')
    truck = models.ForeignKey(TruckHistory, default=None,
                              on_delete=models.CASCADE, related_name='truck_direction')
    place = models.ForeignKey(Place, default=None,
                              on_delete=models.CASCADE, related_name='place_truck_direction')

    takes_time = models.DecimalField(decimal_places=2, max_digits=12)
    amount_km = models.DecimalField(decimal_places=2, max_digits=12)
    emission = models.DecimalField(decimal_places=2, max_digits=12)

    capacity = models.DecimalField(
        decimal_places=2, max_digits=12, blank=True, null=True)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "truck_directions"
        ordering = ['-id']

    def __str__(self):
        return self.truck.name.no_pol + ' | ' + self.place.name
