from datetime import datetime
from django.db import models


class Pds1PlatNoModel(models.Model):
    id = models.AutoField(primary_key=True)
    plat_no = models.CharField(max_length=255)

    created_at = models.DateTimeField(default=datetime.now, blank=True)
    updated_at = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        db_table = "pds1_plat_no"
        ordering = ['-id']

    def __str__(self):
        return self.plat_no
