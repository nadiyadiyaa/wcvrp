from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *


class TruckTypeController():
    def index(request):
        types = TruckType.objects.all()

        return render(request, "master/truck-type/index.html", {
            "types": types
        })

    def add(request):
        return render(request, "master/truck-type/add.html")

    def edit(request, id):
        truck_type = TruckType.objects.get(id=id)

        return render(request, "master/truck-type/edit.html", {
            "truck_type": truck_type
        })

    def submit(request):
        ...

    def update(request):
        ...
