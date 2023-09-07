from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *


class TruckClassController():
    def index(request):
        classes = TruckClass.objects.all()

        return render(request, "master/truck-class/index.html", {
            "classes": classes
        })

    def add(request):
        return render(request, "master/truck-class/add.html")

    def edit(request, id):
        truck_class = TruckClass.objects.get(id=id)

        return render(request, "master/truck-class/edit.html", {
            "truck_class": truck_class
        })

    def submit(request):
        ...

    def update(request):
        ...
