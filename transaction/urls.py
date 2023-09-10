from django.contrib import admin
from django.urls import path
from django.conf.urls import include, handler404

from transaction.controller.RoutePlanningController import *


urlpatterns = [
    path('route-planning', RoutePlanningController.index,
         name='list_route_planning'),

    path('route-planning/<int:id>', RoutePlanningController.edit,
         name='edit_route_planning'),

    path('route-planning/add', RoutePlanningController.create,
         name='add_route_planning'),

    path('route-planning/submit', RoutePlanningController.submit,
         name='submit_route_planning'),

    path('get-truck-direction', RoutePlanningController.get_truck_direction,
         name='get_truck_direction'),
]
