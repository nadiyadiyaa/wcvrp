from django.contrib import admin
from django.urls import path
from django.conf.urls import include, handler404

from transaction.controller.DirectionTrackingController import *


urlpatterns = [
    path('direction-tracking', DirectionTrackingController.index,
         name='direction_tracking'),
]
