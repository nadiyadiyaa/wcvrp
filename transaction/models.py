from datetime import datetime
from django.db import models

from master.models import *


class PlaceCompletement(models.Model):
    id = models.AutoField(primary_key=True)
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
    truck = models.ForeignKey(TruckHistory, default=None,
                              on_delete=models.CASCADE, related_name='truck_direction')
    place = models.ForeignKey(Place, default=None,
                              on_delete=models.CASCADE, related_name='place_truck_direction')
    takes_time = models.DecimalField(decimal_places=2, max_digits=12)
    amount_km = models.DecimalField(decimal_places=2, max_digits=12)
    # emission = models.DecimalField(decimal_places=2, max_digits=12)

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
