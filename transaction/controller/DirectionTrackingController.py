from django.forms import model_to_dict
from master.models import *
from transaction.models import *
from django.db.models import Min

import enum
from django.db.models import Q


class StatusPlace(models.TextChoices):
    YET = 'YET'
    PARTIAL = 'PARTIAL'
    DONE = 'DONE'


class TruckType(models.TextChoices):
    ARMROLL = 1
    DUMP = 2


class Capacity(models.TextChoices):
    ARMROLL = 6.0
    DUMP = 8.0


class DirectionTrackingController():
    def index(request):
        TruckDirection.objects.all().delete()
        TruckHistory.objects.all().delete()
        PlaceCompletement.objects.all().delete()

        process = True
        initDump = False
        velocity = 60/30  # 30km/h
        code_tpa = 'X'
        code_dipo = '0'

        ritation = 1
        truck_id = 1

        truck_type = int(TruckType.ARMROLL.value)
        truck_capacity = float(Capacity.ARMROLL.value)

        temp_capacity = 0
        all_times_needed = 0
        replace_tpa = None

        ex_places = Place.objects.all()
        for ex in ex_places:
            if ex.id not in [1, 2]:
                pc = PlaceCompletement(**{
                    'place_id': ex.id,
                    'rest': ex.volume if ex.volume else 0,
                    'status': StatusPlace.YET,
                })
                pc.save()

        daily_work = SettingWork.objects.get(id=1)
        tpa = Place.objects.filter(nodes=code_tpa).first()
        dipo = Place.objects.filter(nodes=code_dipo).first()

        while process:
            is_finish = PlaceCompletement.objects.filter(
                Q(status=StatusPlace.YET) | Q(status=StatusPlace.PARTIAL)).count()

            if is_finish < 1:
                process = False

            if truck_type is int(TruckType.ARMROLL.value):
                is_dump = PlaceCompletement.objects.filter(
                    Q(status=StatusPlace.YET)).count()
                if is_dump < 1:
                    truck_type = int(TruckType.DUMP.value)
                    truck_capacity = Capacity.DUMP.value

            nearest = None
            params = (
                {'to_place_id': dipo.id} if ritation == 1 else
                {'from_place_id': tpa.id}
            )

            if replace_tpa:
                params = replace_tpa

            prob_nearest = PlaceDistance.objects.filter(**params)
            prob_nearest.annotate(Min("distance")).order_by('distance')

            for prob in prob_nearest:
                from_place_id = prob.from_place_id
                to_place_id = prob.to_place_id

                place_id = from_place_id if ritation == 1 else to_place_id
                place_prob = PlaceCompletement.objects.filter(
                    place_id=place_id).first()

                if place_prob:
                    if truck_type is int(TruckType.ARMROLL.value):
                        if (place_prob.status == StatusPlace.YET.value):
                            nearest = prob
                            break

                    if truck_type is int(TruckType.DUMP.value):
                        if not initDump:
                            TruckHistory.objects.filter(
                                truck_id=truck_id).update(is_complete=True)
                            truck_id += 1
                            initDump = True

                        if place_prob.status == StatusPlace.PARTIAL.value:
                            nearest = prob
                            break

            if nearest:
                place_id = nearest.from_place_id if ritation == 1 else nearest.to_place_id
                type_time = TypeTime.objects.get(type_id=truck_type)
                time_process = type_time.loading_time + type_time.unloading_time
                time_journey = time_process + \
                    (float(nearest.distance) * velocity)

                truck = TruckHistory.objects.filter(
                    truck_id=truck_id)
                exist_truck = truck.first()

                place_prob = PlaceCompletement.objects.filter(
                    place_id=place_id)
                rest = place_prob.first().rest

                tpa_dis = PlaceDistance.objects.filter(
                    from_place_id=1, to_place_id=place_id).first()
                depot_dis = PlaceDistance.objects.filter(
                    from_place_id=1, to_place_id=2).first()

                # TRUCK ARMROLL
                if truck_type is int(TruckType.ARMROLL.value):
                    if rest >= float(truck_capacity):
                        if exist_truck:
                            time_total = float(exist_truck.reach_minutes) + \
                                time_journey

                            if float(time_total) < float(daily_work.minutes):
                                truck.update(
                                    reach_minutes=time_total)

                                up_rest = float(rest) - float(truck_capacity)
                                place_prob.update(rest=up_rest)
                                if up_rest <= 0:
                                    place_prob.update(
                                        status=StatusPlace.DONE.value)

                                dctn = TruckDirection(
                                    truck_id=exist_truck.id,
                                    place_id=place_id,
                                    takes_time=time_journey +
                                    (float(nearest.distance) * velocity),
                                    amount_km=nearest.distance * 2,
                                )
                                dctn.save()

                                ritation += 1
                            else:
                                truck.update(
                                    is_complete=True)
                                ritation = 1
                                truck_id += 1

                        else:
                            truck = TruckHistory(
                                truck_id=truck_id,
                                reach_minutes=time_journey,
                            )
                            truck.save()

                            place_prob.update(rest=float(
                                rest)-float(truck_capacity))

                            tps_to_tpa = PlaceDistance.objects.filter(
                                from_place_id=tpa.id,
                                to_place_id=place_id,
                            ).first()

                            dctn = TruckDirection(
                                truck_id=truck.id,
                                place_id=place_id,
                                takes_time=time_journey +
                                (float(tps_to_tpa.distance) * velocity),
                                amount_km=nearest.distance + tps_to_tpa.distance,
                            )
                            dctn.save()

                            ritation += 1

                    else:
                        place_prob.update(status=StatusPlace.PARTIAL.value)
                        ritation = 1

                # TRUCK DUMP
                elif truck_type is int(TruckType.DUMP.value):
                    time_dump = (float(type_time.loading_time) * float(rest)) + \
                        (float(nearest.distance) * velocity) + \
                        (float(tpa_dis.distance) * velocity) + \
                        (float(depot_dis.distance) * velocity)

                    gap = float(truck_capacity) - float(temp_capacity)
                    isEnough = rest < gap

                    if not exist_truck:
                        exist_truck = TruckHistory(**{
                            'truck_id': truck_id,
                            'reach_minutes': 0,
                            'is_complete': False,
                        })
                        exist_truck.save()

                    reach_minutes = 0
                    if exist_truck:
                        td = TruckDirection.objects.filter(
                            truck_id=exist_truck.id).all()
                        for t in td:
                            reach_minutes += t.takes_time

                    temp_capacity += float(rest) if isEnough else 0
                    all_times_needed = (
                        time_dump +
                        float(reach_minutes) +
                        (float(type_time.unloading_time) * float(temp_capacity))
                    )

                    if float(all_times_needed) < float(daily_work.minutes):
                        if isEnough:
                            check_tpa = TruckDirection.objects.filter(
                                truck_id=exist_truck.id).order_by('-id').first()

                            distance_to_tpa = tpa_dis.distance
                            amount_km = nearest.distance
                            takes_time = (float(
                                type_time.loading_time) * float(rest)) + float(nearest.distance) * velocity

                            if check_tpa:
                                if check_tpa.place_id == 1:
                                    amount_km = distance_to_tpa
                                    takes_time = (
                                        amount_km * 2) + ((rest if isEnough else gap) * type_time.loading_time)

                            place_prob.update(rest=0 if isEnough else gap)
                            tr_direction = TruckDirection(
                                truck_id=exist_truck.id,
                                place_id=place_id,
                                takes_time=takes_time,
                                amount_km=amount_km,
                                capacity=rest if isEnough else gap,
                            )
                            tr_direction.save()

                            place_prob.update(
                                status=StatusPlace.DONE)

                            complete_all = PlaceCompletement.objects.filter(rest__gt=0).\
                                first()
                            if not complete_all:
                                truck.update(
                                    reach_minutes=time_total,
                                    is_complete=True
                                )

                            if place_id == 2:
                                replace_tpa = {'to_place_id': place_id}
                            else:
                                replace_tpa = {'from_place_id': place_id}
                            ritation += 1

                        else:
                            print('___________')
                            takes_time = (float(distance_to_tpa) * velocity)
                            tr_tpa = TruckDirection(
                                truck_id=exist_truck.id,
                                place_id=1,
                                takes_time=takes_time + float(temp_capacity) *
                                type_time.unloading_time,
                                amount_km=distance_to_tpa,
                                capacity=0,
                            )
                            tr_tpa.save()

                            temp_capacity = 0
                            ritation = 1
                            replace_tpa = {'from_place_id': place_id}

                    else:
                        distance_to_tpa = tpa_dis.distance
                        takes_time = (float(distance_to_tpa) * velocity)

                        check_tpa = TruckDirection.objects.filter(
                            truck_id=exist_truck.id).order_by('-id').first()

                        if check_tpa.place_id is not 1:
                            tr_tpa = TruckDirection(
                                truck_id=exist_truck.id,
                                place_id=1,
                                takes_time=(float(
                                    type_time.loading_time) * float(rest)) + float(nearest.distance) * velocity,
                                amount_km=distance_to_tpa,
                                capacity=0,
                            )
                            tr_tpa.save()

                        tr_depot = TruckDirection(
                            truck_id=exist_truck.id,
                            place_id=2,
                            takes_time=float(depot_dis.distance) * velocity,
                            amount_km=float(depot_dis.distance),
                            capacity=0,
                        )
                        tr_depot.save()

                        reach_minutes = 0
                        if exist_truck:
                            td = TruckDirection.objects.filter(
                                truck_id=exist_truck.id).all()
                            for t in td:
                                reach_minutes += t.takes_time

                        TruckHistory.objects.filter(truck_id=truck_id).update(
                            reach_minutes=reach_minutes,
                            is_complete=True,
                        )

                        temp_capacity = 0
                        all_times_needed = 0
                        ritation = 1
                        replace_tpa = None

                        truck_id += 1
