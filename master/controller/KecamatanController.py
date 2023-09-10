from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

from master.models import *
from django.contrib import messages


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

    @csrf_exempt
    @require_http_methods(["POST"])
    def submit(request):
        kecamatan = Kecamatan(name=request.POST['name'])
        kecamatan.save()

        messages.success(request, "Success create kecamatan!")
        return redirect('list_kecamatan')

    @csrf_exempt
    @require_http_methods(["POST"])
    def update(request):
        id = int(request.POST['id'])
        name = request.POST['name']

        kecamatan = Kecamatan.objects.filter(id=id)
        kecamatan.update(name=name)

        messages.success(request, "Success update kecamatan!")
        return redirect('list_kecamatan')
