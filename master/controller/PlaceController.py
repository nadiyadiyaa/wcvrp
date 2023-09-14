from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib import messages

from django.http.response import HttpResponse
from master.models import *


class PlaceController():
    def index(request):
        place = Place.objects.order_by('id')
        # return HttpResponse(place)

        return render(request, "master/place/index.html", {
            'title': 'Place',
            "place": place
        })

    def add(request):
        return render(request, "master/place/add.html", {
            'title': 'Add Place',
        })

    def edit(request, id):
        place = Place.objects.get(id=id)

        return render(request, "master/place/edit.html", {
            'title': 'Detail Place',
            "place": place
        })

    @csrf_exempt
    @require_http_methods(["POST"])
    def submit(request):
        name = request.POST['name']
        location = request.POST['location']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
        volume = request.POST['volume']

        last_place = Place.objects.all().order_by('id').last()
        place = Place(
            nodes=str(int(last_place.nodes) + 1),
            name=name,
            location=location,
            latitude=latitude,
            longitude=longitude,
            volume=volume,
        )
        place.save()

        messages.success(request, "Success create place!")
        return redirect("list_place")

    @csrf_exempt
    @require_http_methods(["POST"])
    def update(request):
        id = int(request.POST['id'])
        name = request.POST['name']
        location = request.POST['location']
        latitude = request.POST['latitude']
        longitude = request.POST['longitude']
        volume = request.POST['volume']

        place = Place.objects.filter(id=id)
        place.update(
            name=name,
            location=location,
            latitude=latitude,
            longitude=longitude,
            volume=volume,
        )

        messages.success(request, "Success update place!")
        return redirect("list_place")
