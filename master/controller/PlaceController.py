from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib import messages

from master.models import *


class PlaceController():
    def index(request):
        place = Place.objects.all()

        return render(request, "master/place/index.html", {
            "place": place
        })

    def add(request):
        return render(request, "master/place/add.html")

    def edit(request, id):
        place = Place.objects.get(id=id)

        return render(request, "master/place/edit.html", {
            "place": place
        })

    @csrf_exempt
    @require_http_methods(["POST"])
    def submit(request):
        place = Place(**dict(request.POST.items()))
        place.save()

        messages.success(request, "Success create place!")
        return redirect("list_place")

    @csrf_exempt
    @require_http_methods(["POST"])
    def update(request):
        ...
