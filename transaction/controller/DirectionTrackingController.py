from master.models import *
from transaction.models import *
import enum


class EnumTruckType(models.TextChoices):
    ARMROLL = 1
    DUMP = 2


class DirectionTrackingController():
    def index(request):
        ex_places = Place.objects.all()
        for ex in ex_places:
            pc = PlaceCompletement(**{
                'place_id': ex.id,
                'rest': ex.volume,
                'is_complete': False,
            })
            pc.save()

        ex_trucks = Truck.objects.all()
        for ex in ex_trucks:
            setting = SettingWork.objects.get(pk=1)
            tr = TruckHistory(**{
                'truck_id': ex.id,
                'rest_minutes': setting.minutes,
                'is_complete': False,
            })
            tr.save()

        trucks = Truck.object.all()
        for tr in trucks:
            next_place = None
            if tr is EnumTruckType.ARMROLL.value:
                next_place = PlaceDistance.objects.filter(to_place_id=2)
            ...
