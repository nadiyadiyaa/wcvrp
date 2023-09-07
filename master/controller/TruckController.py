from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *


class TruckController():
    def index(request):
        truck = Truck.objects.all()

        return render(request, "master/truck/index.html", {
            "truck": truck
        })

    def add(request):
        kecamatan = Kecamatan.objects.all()
        truck_type = TruckType.objects.all()
        truck_class = TruckClass.objects.all()

        return render(request, "master/truck/add.html", {
            "kecamatan": kecamatan,
            "truck_type": truck_type,
            "truck_class": truck_class,
        })

    def edit(request, id):
        kecamatan = Kecamatan.objects.all()
        truck_type = TruckType.objects.all()
        truck_class = TruckClass.objects.all()
        truck = Truck.objects.get(id=id)

        return render(request, "master/truck/edit.html", {
            "kecamatan": kecamatan,
            "truck_type": truck_type,
            "truck_class": truck_class,
            "truck": truck
        })

    def submit(request):
        ...

    def update(request):
        ...
