from master.models import *
from transaction.models import *
from django.db.models import Min

import enum
from django.db.models import Q


class EnumStatusPlace(models.TextChoices):
    YET = 'YET'
    PARTIAL = 'PARTIAL'
    DONE = 'DONE'


class EnumTruckType(models.TextChoices):
    ARMROLL = 1
    DUMP = 2


class EnumCapacity(models.TextChoices):
    ARMROLL = 6.0
    DUMP = 8.0


class DirectionTrackingController():
    def index(request):
        # delete complementt
        PlaceCompletement.objects.all().delete()

        process = True
        velocity = 60/30  # 30km/h
        code_tpa = 'X'
        code_dipo = '0'

        ritation = 1
        truck_id = 1
        truck_type = int(EnumTruckType.ARMROLL.value)
        truck_capacity = float(EnumCapacity.ARMROLL.value)

        # Initialize Place
        ex_places = Place.objects.all()
        for ex in ex_places:
            pc = PlaceCompletement(**{
                'place_id': ex.id,
                'rest': ex.volume if ex.volume else 0,
                'status': EnumStatusPlace.YET,
            })
            pc.save()

        # General Setup
        daily_work = SettingWork.objects.get(id=1)

        # Set TPA & Dipo
        tpa = Place.objects.filter(nodes=code_tpa).first()
        dipo = Place.objects.filter(nodes=code_dipo).first()

        # Dynamic variable (ritation and truck type)
        nearest_id = dipo.id if ritation == 1 else tpa.id

        while process:
            # Check if finish or not
            is_finish = PlaceCompletement.objects.filter(
                Q(status=EnumStatusPlace.YET) | Q(status=EnumStatusPlace.PARTIAL)).count()

            if is_finish < 1:
                process = False
                return

            # Check if still YET or not
            if truck_type is int(EnumTruckType.ARMROLL.value):
                is_dump = PlaceCompletement.objects.filter(
                    Q(status=EnumStatusPlace.YET)).count()
                if is_dump < 1:
                    truck_type = int(EnumTruckType.DUMP.value)
                    truck_capacity = int(EnumCapacity.DUMP.value)

            nearest = None
            prob_nearest = PlaceDistance.objects.filter(to_place_id=nearest_id).\
                annotate(Min("distance")).\
                order_by('distance')

            # Get Valid Place
            for prob in prob_nearest:
                place_prob = PlaceCompletement.objects.get(
                    place_id=prob.from_place_id)

                if truck_type == int(EnumTruckType.ARMROLL.value):
                    if (
                        (place_prob.status != EnumStatusPlace.PARTIAL.value) and
                        (place_prob.status != EnumStatusPlace.DONE.value)
                    ):
                        # print("ketemu nearest!!!!")
                        nearest = prob
                        break

                if truck_type == int(EnumTruckType.DUMP.value):
                    if (place_prob.status == EnumStatusPlace.PARTIAL.value):
                        nearest = prob
                        break

            place_prob = PlaceCompletement.objects.filter(
                place_id=nearest.from_place_id)
            rest = place_prob.first().rest

            print(f'rest: {rest}')
            print(f'nearest : {nearest}')
            print(f'ritation : {ritation}')

            if rest >= float(truck_capacity):
                type_time = TypeTime.objects.get(type_id=truck_type)
                time_process = type_time.loading_time + type_time.unloading_time
                time_journey = time_process + \
                    (float(nearest.distance) * velocity)

                check_avail_time = TruckHistory.objects.filter(
                    truck_id=truck_id).first()

                if check_avail_time:
                    # print("masuk sini / udah ada record!!!!")
                    time_total = check_avail_time.reach_minutes + \
                        time_journey + (float(nearest.distance) * velocity)
                    tr_history = TruckHistory.objects.filter(
                        truck_id=truck_id)

                    if float(time_total) < float(daily_work.minutes):
                        # print(f'time total : {time_total}')

                        tr_history.update(
                            reach_minutes=time_total)

                        place_prob.update(rest=float(
                            rest)-float(truck_capacity))

                        # Add Truck To Direction
                        dctn = TruckDirection(
                            truck_id=tr_history.first().id,
                            place_id=nearest.from_place_id,
                            takes_time=time_total,
                            amount_km=nearest.distance,
                        )
                        dctn.save()

                        ritation += 1
                    else:
                        tr_history.update(
                            is_complete=True)
                        ritation = 1
                        truck_id += 1

                else:
                    # print("masuk sini / belum ada record")
                    tr_history = TruckHistory(
                        truck_id=truck_id,
                        reach_minutes=time_journey,
                        is_complete=False,
                        created_at=datetime.now(),
                        modified_at=datetime.now()
                    )
                    tr_history.save()

                    place_prob.update(rest=float(
                        rest)-float(truck_capacity))

                    # Add Truck To Direction
                    dctn = TruckDirection(
                        truck_id=tr_history.id,
                        place_id=nearest.from_place_id,
                        takes_time=time_journey,
                        amount_km=nearest.distance,
                    )
                    dctn.save()

                    ritation += 1

            else:
                # print("Sisa gabisa masuk")
                place_prob.update(status=EnumStatusPlace.PARTIAL.value)
                ritation += 1
