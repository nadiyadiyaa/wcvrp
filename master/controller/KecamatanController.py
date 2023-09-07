from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *


class KecamatanController():
    def index(request):
        kecamatan = Kecamatan.objects.all()

        return render(request, "master/kecamatan/index.html", {
            "kecamatan": kecamatan
        })

    def add(request):
        return render(request, "master/kecamatan/add.html")

    def edit(request, id):
        kecamatan = Kecamatan.objects.get(id=id)

        return render(request, "master/kecamatan/edit.html", {
            "kecamatan": kecamatan
        })

    def submit(request):
        ...

    def update(request):
        ...
