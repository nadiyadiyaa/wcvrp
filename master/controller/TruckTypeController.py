from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *
from django.contrib import messages


class TruckTypeController():
    def index(request):
        types = TruckType.objects.all()

        return render(request, "master/truck-type/index.html", {
            'title': 'Truck Type',
            "types": types
        })

    def edit(request, id):
        truck_type = TruckType.objects.get(id=id)

        return render(request, "master/truck-type/edit.html", {
            'title': 'Add Truck Type',
            "truck_type": truck_type
        })

    @csrf_exempt
    @require_http_methods(["POST"])
    def update(request):
        id = int(request.POST['id'])
        truck_type = request.POST['truck_type']
        capacity = request.POST['capacity']

        type = TruckType.objects.filter(id=id)
        type.update(
            truck_type=truck_type,
            capacity=capacity,
        )

        messages.success(request, "Success update truck type!")
        return redirect('list_truck_type')
