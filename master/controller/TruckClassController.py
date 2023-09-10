from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *
from django.contrib import messages


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

    @csrf_exempt
    @require_http_methods(["POST"])
    def submit(request):
        truck_class = TruckClass(classes=request.POST['classes'])
        truck_class.save()

        messages.success(request, "Success create truck class!")
        return redirect('list_truck_class')

    @csrf_exempt
    @require_http_methods(["POST"])
    def update(request):
        id = int(request.POST['id'])
        classes = request.POST['classes']

        truck_class = TruckClass.objects.filter(id=id)
        truck_class.update(classes=classes)

        messages.success(request, "Success update truck class!")
        return redirect('list_truck_class')
