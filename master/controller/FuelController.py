from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *
from django.contrib import messages


class FuelController():
    def index(request):
        fuels = Fuel.objects.all()

        return render(request, "master/fuel/index.html", {
            "fuels": fuels
        })

    def add(request):
        return render(request, "master/fuel/add.html")

    def edit(request, id):
        fuel = Fuel.objects.get(id=id)

        return render(request, "master/fuel/edit.html", {
            "fuel": fuel
        })

    @csrf_exempt
    @require_http_methods(["POST"])
    def submit(request):
        fuel = Fuel(
            fuel_name=request.POST['fuel_name'],
            ems_factor=request.POST['ems_factor'],
        )
        fuel.save()

        messages.success(request, "Success create fuel!")
        return redirect('list_fuel')

    @csrf_exempt
    @require_http_methods(["POST"])
    def update(request):
        id = int(request.POST['id'])
        fuel_name = request.POST['fuel_name']
        ems_factor = request.POST['ems_factor']

        fuel = Fuel.objects.filter(id=id)
        fuel.update(
            fuel_name=fuel_name,
            ems_factor=ems_factor,
        )

        messages.success(request, "Success update fuel!")
        return redirect('list_fuel')
