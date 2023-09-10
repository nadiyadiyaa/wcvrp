from django.contrib import admin
from django.urls import path
from django.conf.urls import include, handler404

from master.controller.DashboardController import *
from master.controller.KecamatanController import *
from master.controller.PlaceController import *
from master.controller.TruckTypeController import *
from master.controller.TruckClassController import *
from master.controller.TruckController import *
from master.controller.FuelController import *


urlpatterns = [
    path('', DashboardController.index, name='dashboard'),

    path('kecamatan', KecamatanController.index, name='list_kecamatan'),
    path('kecamatan/<int:id>', KecamatanController.edit, name='edit_kecamatan'),
    path('kecamatan/add', KecamatanController.add, name='add_kecamatan'),
    path('kecamatan/submit', KecamatanController.submit, name='submit_kecamatan'),
    path('kecamatan/update', KecamatanController.update, name='update_kecamatan'),

    path('place', PlaceController.index, name='list_place'),
    path('place/<int:id>', PlaceController.edit, name='edit_place'),
    path('place/add', PlaceController.add, name='add_place'),
    path('place/submit', PlaceController.submit, name='submit_place'),
    path('place/update', PlaceController.update, name='update_place'),

    path('fuel', FuelController.index, name='list_fuel'),
    path('fuel/<int:id>', FuelController.edit, name='edit_fuel'),
    path('fuel/add', FuelController.add, name='add_fuel'),
    path('fuel/submit', FuelController.submit, name='submit_fuel'),
    path('fuel/update', FuelController.update, name='update_fuel'),

    path('truck-type', TruckTypeController.index, name='list_truck_type'),
    path('truck-type/<int:id>', TruckTypeController.edit, name='edit_truck_type'),
    path('truck-type/update', TruckTypeController.update, name='update_truck_type'),

    path('truck-class', TruckClassController.index, name='list_truck_class'),
    path('truck-class/<int:id>', TruckClassController.edit, name='edit_truck_class'),
    path('truck-class/add', TruckClassController.add, name='add_truck_class'),
    path('truck-class/submit', TruckClassController.submit,
         name='submit_truck_class'),
    path('truck-class/update', TruckClassController.update,
         name='update_truck_class'),

    path('truck', TruckController.index, name='list_truck'),
    path('truck/<int:id>', TruckController.edit, name='edit_truck'),
    path('truck/add', TruckController.add, name='add_truck'),
    path('truck/submit', TruckController.submit, name='submit_truck'),
    path('truck/update', TruckController.update, name='update_truck'),
]
