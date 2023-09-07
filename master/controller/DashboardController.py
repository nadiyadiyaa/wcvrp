from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *


class DashboardController():
    def index(request):
        c_kecamatan = Kecamatan.objects.count()
        c_place = Place.objects.count()
        c_truck = Truck.objects.count()

        return render(request, "index.html", {
            'c_kecamatan': c_kecamatan,
            'c_place': c_place,
            'c_truck': c_truck,
        })
