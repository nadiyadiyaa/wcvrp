from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *
from django.contrib import messages


class TruckController():
    def index(request):
        truck = Truck.objects.all()

        return render(request, "master/truck/index.html", {
            'title': 'Truck',
            "truck": truck
        })

    def add(request):
        kecamatan = Kecamatan.objects.all()
        truck_type = TruckType.objects.all()
        truck_class = TruckClass.objects.all()

        return render(request, "master/truck/add.html", {
            'title': 'Add Truck',
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
            'title': 'Detail Truck',
            "kecamatan": kecamatan,
            "truck_type": truck_type,
            "truck_class": truck_class,
            "truck": truck
        })

    @csrf_exempt
    @require_http_methods(["POST"])
    def submit(request):
        kecamatan_id = int(request.POST['kecamatan_id'])
        type_id = int(request.POST['type_id'])
        truck_class_id = int(request.POST['truck_class_id'])
        no_pol = request.POST['no_pol']
        year = request.POST['year']
        consumption = request.POST['consumption']

        truck = Truck(
            kecamatan_id=kecamatan_id,
            type_id=type_id,
            truck_class_id=truck_class_id,
            no_pol=no_pol,
            year=year,
        )
        truck.save()

        messages.success(request, "Success create truck!")
        return redirect("list_truck")

    @csrf_exempt
    @require_http_methods(["POST"])
    def update(request):
        id = int(request.POST['id'])
        kecamatan_id = int(request.POST['kecamatan_id'])
        type_id = int(request.POST['type_id'])
        truck_class_id = int(request.POST['truck_class_id'])
        no_pol = request.POST['no_pol']
        year = request.POST['year']

        truck = Truck.objects.filter(id=id)
        truck.update(
            kecamatan_id=kecamatan_id,
            type_id=type_id,
            truck_class_id=truck_class_id,
            no_pol=no_pol,
            year=year,
        )

        messages.success(request, "Success update truck!")
        return redirect("list_truck")
