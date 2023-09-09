from django.forms import model_to_dict
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
        TruckDirection.objects.all().delete()
        TruckHistory.objects.all().delete()
        PlaceCompletement.objects.all().delete()

        process = True
        velocity = 60/30  # 30km/h
        code_tpa = 'X'
        code_dipo = '0'

        ritation = 1
        truck_id = 1
        truck_type = int(EnumTruckType.ARMROLL.value)
        truck_capacity = float(EnumCapacity.ARMROLL.value)

        temp_capacity = 0
        all_times_needed = 0
        replace_tpa = None

        # Initialize Place
        ex_places = Place.objects.all()
        for ex in ex_places:
            if ex.id not in [1, 2]:
                pc = PlaceCompletement(**{
                    'place_id': ex.id,
                    'rest': ex.volume if ex.volume else 0,
                    'status': EnumStatusPlace.YET,
                })
                pc.save()

        daily_work = SettingWork.objects.get(id=1)
        tpa = Place.objects.filter(nodes=code_tpa).first()
        dipo = Place.objects.filter(nodes=code_dipo).first()

        while process:
            is_finish = PlaceCompletement.objects.filter(
                Q(status=EnumStatusPlace.YET) | Q(status=EnumStatusPlace.PARTIAL)).count()

            if is_finish < 1:
                process = False
                # return

            if truck_type is int(EnumTruckType.ARMROLL.value):
                is_dump = PlaceCompletement.objects.filter(
                    Q(status=EnumStatusPlace.YET)).count()
                if is_dump < 1:
                    truck_type = int(EnumTruckType.DUMP.value)
                    truck_capacity = EnumCapacity.DUMP.value

            nearest = None
            params = (
                {'to_place_id': dipo.id} if ritation == 1 else
                {'from_place_id': tpa.id}
            )

            if replace_tpa:
                params = replace_tpa
                print(replace_tpa)

            prob_nearest = PlaceDistance.objects.filter(**params)
            prob_nearest.annotate(Min("distance")).order_by('distance')

            for prob in prob_nearest:
                if truck_type == int(EnumTruckType.DUMP.value):
                    print(f'truck_id : {truck_id}')
                    print(f'from_place_id : {prob.from_place_id}')
                    print(f'to_place_id : {prob.to_place_id}')

                from_place_id = prob.from_place_id
                to_place_id = prob.to_place_id

                place_id = from_place_id if ritation == 1 else to_place_id
                place_prob = PlaceCompletement.objects.filter(
                    place_id=place_id).first()

                if place_prob:
                    if truck_type == int(EnumTruckType.ARMROLL.value):
                        if (
                            (place_prob.status != EnumStatusPlace.PARTIAL.value) and
                            (place_prob.status != EnumStatusPlace.DONE.value)
                        ):
                            nearest = prob
                            break

                    if truck_type == int(EnumTruckType.DUMP.value):
                        if (
                            (place_prob.status == EnumStatusPlace.PARTIAL.value)
                        ):
                            nearest = prob
                            break

            if nearest:
                type_time = TypeTime.objects.get(type_id=truck_type)
                time_process = type_time.loading_time + type_time.unloading_time
                time_journey = time_process + \
                    (float(nearest.distance) * velocity)

                if truck_type == int(EnumTruckType.ARMROLL.value):
                    place_prob = PlaceCompletement.objects.filter(
                        place_id=nearest.from_place_id if ritation == 1 else nearest.to_place_id)
                    rest = place_prob.first().rest

                    if rest >= float(truck_capacity):
                        check_avail_time = TruckHistory.objects.filter(
                            truck_id=truck_id).first()

                        if check_avail_time:
                            # print("masuk sini / udah ada record!!!!")
                            time_total = check_avail_time.reach_minutes + \
                                time_journey
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
                                    place_id=nearest.from_place_id if ritation == 1 else nearest.to_place_id,
                                    takes_time=time_journey +
                                    (float(nearest.distance) * velocity),
                                    amount_km=nearest.distance * 2,
                                )
                                dctn.save()

                                ritation += 1
                            else:
                                tr_history.update(
                                    is_complete=True)
                                ritation = 1
                                truck_id += 1

                        else:
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

                            tps_to_tpa = PlaceDistance.objects.filter(
                                from_place_id=tpa.id,
                                to_place_id=nearest.from_place_id if ritation == 1 else nearest.to_place_id,
                            ).first()

                            dctn = TruckDirection(
                                truck_id=tr_history.id,
                                place_id=nearest.from_place_id if ritation == 1 else nearest.to_place_id,
                                takes_time=time_journey +
                                (float(tps_to_tpa.distance) * velocity),
                                amount_km=nearest.distance + tps_to_tpa.distance,
                            )
                            dctn.save()

                            ritation += 1

                    else:
                        place_prob.update(status=EnumStatusPlace.PARTIAL.value)
                        ritation = 1
                        # ritation += 1

                if truck_type == int(EnumTruckType.DUMP.value):
                    tr_history = TruckHistory.objects.filter(
                        truck_id=truck_id).first()

                    time_dump = type_time.loading_time + \
                        (float(nearest.distance) * velocity)
                    capacity = PlaceCompletement.objects.filter(
                        place_id=nearest.from_place_id if ritation == 1 else nearest.to_place_id)

                    rest = capacity.first().rest
                    gap = float(truck_capacity) - \
                        float(temp_capacity)
                    isEnough = rest < gap

                    print(f'terakhiran : {tr_history}')

                    if not tr_history:
                        tr_history = TruckHistory(**{
                            'truck_id': truck_id,
                            'is_complete': False,
                            'created_at': datetime.now(),
                            'modified_at': datetime.now()
                        })

                        tr_history.save()

                    temp_capacity += float(rest) if isEnough else float(gap)
                    all_times_needed += time_dump + type_time.unloading_time

                    if float(all_times_needed) < float(daily_work.minutes):
                        if isEnough:
                            capacity.update(rest=0 if isEnough else gap)

                            tr_direction = TruckDirection(
                                truck_id=tr_history.id,
                                place_id=nearest.from_place_id if ritation == 1 else nearest.to_place_id,
                                takes_time=time_dump,
                                amount_km=nearest.distance,
                                capacity=rest if isEnough else gap,
                                created_at=datetime.now(),
                                modified_at=datetime.now()
                            )
                            tr_direction.save()

                            capacity.update(
                                status=EnumStatusPlace.DONE)

                            print(model_to_dict(nearest))
                            change_tpa_id = nearest.from_place_id if ritation == 1 else nearest.to_place_id
                            if change_tpa_id == 2:
                                replace_tpa = {'to_place_id': change_tpa_id}
                            else:
                                replace_tpa = {'from_place_id': change_tpa_id}
                            # print(f'tpa_change : {change_tpa_id}')

                            ritation += 1
                            # print(f'place : {model_to_dict(place)}')
                            # print(f'ritation : {ritation}')
                            # print("success create truck direction ../")

                    else:
                        TruckHistory.objects.filter(truck_id=truck_id).update(
                            reach_minutes=all_times_needed - time_dump + type_time.unloading_time,
                            is_complete=True,
                        )

                        temp_capacity = 0
                        all_times_needed = 0
                        ritation = 1
                        replace_tpa = None
                        truck_id += 1
                        # print("success create truck history ../")

            else:
                print('gagal maning! ...')
