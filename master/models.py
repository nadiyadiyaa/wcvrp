from datetime import datetime
from django.db import models


class SettingWork(models.Model):
    id = models.AutoField(primary_key=True)
    minutes = models.IntegerField()
    velocity_per_h = models.IntegerField()

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "setting_works"
        ordering = ['-id']

    def __str__(self):
        return self.minutes


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    nodes = models.CharField(unique=True, max_length=200)

    name = models.CharField(max_length=200)
    location = models.TextField()

    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    volume = models.DecimalField(
        decimal_places=2, max_digits=12, null=True, blank=True)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "places"
        ordering = ['-id']

    def __str__(self):
        return self.nodes + ' | ' + self.name


class PlaceDistance(models.Model):
    id = models.AutoField(primary_key=True)
    from_place = models.ForeignKey(Place, default=None,
                                   on_delete=models.CASCADE, related_name='from_place')
    to_place = models.ForeignKey(Place, default=None,
                                 on_delete=models.CASCADE, related_name='to_place')
    distance = models.DecimalField(decimal_places=2, max_digits=12)
    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "place_distances"
        ordering = ['-id']

    def __str__(self):
        return self.from_place.name + ' | ' + self.to_place.name


class Kecamatan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "kecamatans"
        ordering = ['-id']

    def __str__(self):
        return self.name


class TruckClass(models.Model):
    id = models.AutoField(primary_key=True)
    classes = models.CharField(max_length=200)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "truck_classes"
        ordering = ['-id']

    def __str__(self):
        return self.classes


class TruckType(models.Model):
    id = models.AutoField(primary_key=True)
    truck_type = models.CharField(max_length=200)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "truck_types"
        ordering = ['-id']

    def __str__(self):
        return self.truck_type


class Fuel(models.Model):
    id = models.AutoField(primary_key=True)

    fuel_name = models.CharField(max_length=200)
    ems_factor = models.DecimalField(decimal_places=2, max_digits=12)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "feuls"
        ordering = ['-id']

    def __str__(self):
        return self.fuel_name


class TypeTime(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(TruckType, default=None,
                             on_delete=models.CASCADE)

    loading_time = models.IntegerField()
    unloading_time = models.IntegerField()
    consumption = models.DecimalField(decimal_places=2, max_digits=12)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "type_times"
        ordering = ['-id']

    def __str__(self):
        return self.type.truck_type


class Truck(models.Model):
    id = models.AutoField(primary_key=True)
    kecamatan = models.ForeignKey(Kecamatan, default=None,
                                  on_delete=models.CASCADE, related_name='kecamatan')
    type = models.ForeignKey(TruckType, default=None,
                             on_delete=models.CASCADE, related_name='type')
    truck_class = models.ForeignKey(TruckClass, default=None,
                                    on_delete=models.CASCADE, related_name='truck_class')

    no_pol = models.CharField(max_length=255)
    year = models.CharField(max_length=255)

    capacity = models.DecimalField(decimal_places=2, max_digits=12)

    created_at = models.DateTimeField(
        default=datetime.now, null=True)
    created_by = models.CharField(max_length=200, blank=True)
    modified_at = models.DateTimeField(
        default=datetime.now, null=True)
    modified_by = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "trucks"
        ordering = ['-id']

    def __str__(self):
        return self.no_pol + ' | ' + type.truck_type
