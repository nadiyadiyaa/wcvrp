from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from django.forms import model_to_dict
from django.db.models import Sum
from django.http.response import JsonResponse
from django.db.models import Q
from django.shortcuts import redirect, render

from master.models import *
from transaction.models import *
from django.db.models import Min


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


class RoutePlanningController():
    def index(request):
        rp = MainTrial.objects.all()

        return render(request,
                      "transaction/route-planning/index.html",
                      {
                          "rp": rp,
                      })

    def create(request):
        velocity = SettingWork.objects.all().first()
        fuel = Fuel.objects.all()
        armroll = TypeTime.objects.get(type_id=1)
        dump = TypeTime.objects.get(type_id=2)

        return render(request,
                      "transaction/route-planning/add.html",
                      {
                          "velocity": velocity.velocity_per_h,
                          "fuel": fuel,
                          "armroll": armroll,
                          "dump": dump,
                      })

    def edit(request, id):
        main = MainTrial.objects.get(pk=id)
        c_exist_truck = Truck.objects.count()
        c_truck = TruckHistory.objects.filter(
            mtrial_id=id).count()

        fuel = Fuel.objects.all()
        truck_history = TruckHistory.objects.filter(
            mtrial_id=id).order_by('truck_id')

        total_emision = 0
        total_distance = 0
        for history in truck_history:
            direction = history.truck_direction.all()
            for dir in direction:
                total_emision += dir.emission
                total_distance += dir.amount_km

        return render(request,
                      "transaction/route-planning/edit.html",
                      {
                          'c_distance': total_distance,
                          'c_emission': total_emision,
                          'c_exist_truck': c_exist_truck,
                          'c_truck': c_truck,
                          'main': main,
                          "fuel": fuel,
                          'truck_history': truck_history
                      })

    @csrf_exempt
    @require_http_methods(["POST"])
    def submit(request):
        setting = SettingWork.objects.all().first()
        # Describe Parameter
        q_name = request.POST.get('name', f'TEST__{datetime.now()}')
        q_desc = request.POST.get('short_desc', '')

        q_loading_armroll = request.POST.get('loading_armroll', None)
        q_unloading_armroll = request.POST.get('unloading_armroll', None)
        q_loading_dump = request.POST.get('loading_dump', None)
        q_unloading_dump = request.POST.get('unloading_dump', None)

        q_fuel = request.POST.get('fuel_id', 2)
        q_velocity = request.POST.get('velocity', setting.velocity_per_h)
        velocity = 60 / float(q_velocity)

        process = True
        initDump = False

        ID_TPA = 1
        ID_DIPO = 2

        code_tpa = 'X'
        code_dipo = '0'

        ritation = 1
        truck_id = 1

        truck_type = int(TruckType.ARMROLL.value)
        truck_capacity = float(Capacity.ARMROLL.value)

        temp_capacity = 0
        all_times_needed = 0
        replace_tpa = None

        mtrial = MainTrial(
            name=q_name,
            short_desc=q_desc,
            fuel_id=q_fuel,
            velocity=velocity,
            loading_armroll=q_loading_armroll,
            unloading_armroll=q_unloading_armroll,
            loading_dump=q_loading_dump,
            unloading_dump=q_unloading_dump,
        )
        mtrial.save()

        ex_places = Place.objects.all()
        for ex in ex_places:
            if ex.id not in [ID_TPA, ID_DIPO]:
                pc = PlaceCompletement(**{
                    'mtrial_id': mtrial.pk,
                    'place_id': ex.id,
                    'rest': ex.volume if ex.volume else 0,
                    'status': StatusPlace.YET,
                })
                pc.save()

        tpa = Place.objects.filter(nodes=code_tpa).first()
        dipo = Place.objects.filter(nodes=code_dipo).first()

        while process:
            is_finish = PlaceCompletement.objects.filter(mtrial_id=mtrial.pk).filter(
                Q(status=StatusPlace.YET) | Q(status=StatusPlace.PARTIAL)).count()

            if is_finish < 1:
                process = False

            if truck_type is int(TruckType.ARMROLL.value):
                is_dump = PlaceCompletement.objects.filter(mtrial_id=mtrial.pk).\
                    filter(Q(status=StatusPlace.YET)).count()
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
                    mtrial_id=mtrial.pk, place_id=place_id).first()

                if place_prob:
                    if truck_type is int(TruckType.ARMROLL.value):
                        if (place_prob.status == StatusPlace.YET.value):
                            nearest = prob
                            break

                    if truck_type is int(TruckType.DUMP.value):
                        if not initDump:
                            TruckHistory.objects.filter(
                                mtrial_id=mtrial.pk, truck_id=truck_id).update(is_complete=True)
                            truck_id += 1
                            initDump = True

                        if place_prob.status == StatusPlace.PARTIAL.value:
                            nearest = prob
                            break

            if nearest:
                type_time = TypeTime.objects.get(type_id=truck_type)
                loading_time = type_time.loading_time
                unloading_time = type_time.unloading_time

                place_id = nearest.from_place_id if ritation == 1 else nearest.to_place_id

                truck = TruckHistory.objects.filter(
                    mtrial_id=mtrial.pk, truck_id=truck_id)
                exist_truck = truck.first()

                place_prob = PlaceCompletement.objects.filter(
                    mtrial_id=mtrial.pk, place_id=place_id)
                rest = place_prob.first().rest

                tpa_dis = PlaceDistance.objects.filter(
                    from_place_id=ID_TPA,
                    to_place_id=place_id).first()

                depot_dis = PlaceDistance.objects.filter(
                    from_place_id=ID_TPA,
                    to_place_id=ID_DIPO).first()

                fuel_factor = Fuel.objects.get(pk=q_fuel)

                # TRUCK ARMROLL
                if truck_type is int(TruckType.ARMROLL.value):
                    if q_loading_armroll:
                        loading_time = float(q_loading_armroll)
                    if q_unloading_armroll:
                        unloading_time = float(q_unloading_armroll)

                    time_journey = (float(nearest.distance) *
                                    velocity) + loading_time + unloading_time

                    if rest >= float(truck_capacity):
                        if exist_truck:
                            time_total = float(exist_truck.reach_minutes) + \
                                time_journey

                            if float(time_total) < float(setting.minutes):
                                truck.update(
                                    reach_minutes=time_total)

                                up_rest = float(rest) - float(truck_capacity)
                                place_prob.update(rest=up_rest)
                                if up_rest <= 0:
                                    place_prob.update(
                                        status=StatusPlace.DONE.value)

                                dctn = TruckDirection(
                                    mtrial_id=mtrial.pk,
                                    truck_id=exist_truck.id,
                                    place_id=place_id,
                                    takes_time=(
                                        time_journey +
                                        (float(nearest.distance) * velocity)
                                    ),
                                    capacity=6.0,
                                    amount_km=nearest.distance * 2,
                                    emission=(
                                        (nearest.distance * 2) *
                                        (fuel_factor.ems_factor) *
                                        (type_time.consumption)
                                    )
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
                                mtrial_id=mtrial.pk,
                                type_id=truck_type,
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
                                mtrial_id=mtrial.pk,
                                truck_id=truck.id,
                                place_id=place_id,
                                takes_time=(
                                    time_journey +
                                    (float(tps_to_tpa.distance) * velocity)
                                ),
                                capacity=6.0,
                                amount_km=(nearest.distance +
                                           tps_to_tpa.distance),
                                emission=(
                                    (nearest.distance + tps_to_tpa.distance) *
                                    (fuel_factor.ems_factor) *
                                    (type_time.consumption)
                                )
                            )
                            dctn.save()
                            ritation += 1

                    else:
                        place_prob.update(status=StatusPlace.PARTIAL.value)
                        ritation = 1

                # TRUCK DUMP
                elif truck_type is int(TruckType.DUMP.value):
                    if q_loading_dump:
                        loading_time = float(q_loading_dump)
                    if q_unloading_dump:
                        unloading_time = float(q_unloading_dump)

                    gap = float(truck_capacity) - float(temp_capacity)
                    isEnough = rest < gap

                    if not exist_truck:
                        exist_truck = TruckHistory(**{
                            'mtrial_id': mtrial.pk,
                            'type_id': truck_type,
                            'truck_id': truck_id,
                            'reach_minutes': 0,
                        })
                        exist_truck.save()

                    temp_capacity += float(rest) if isEnough else 0
                    time_dump = (
                        (float(loading_time) * float(rest)) +
                        (float(nearest.distance) * velocity) +
                        (float(tpa_dis.distance) * velocity) +
                        (float(depot_dis.distance) * velocity)
                    )

                    sum_truck = TruckDirection.objects.filter(
                        mtrial_id=mtrial.pk,
                        truck_id=exist_truck.id
                    ).\
                        aggregate(
                            takes_time=Sum('takes_time'),
                            capacity=Sum('capacity')
                    )

                    takes_time = sum_truck['takes_time']
                    capacity = sum_truck['capacity']

                    all_times_needed = (
                        time_dump +
                        float(takes_time if takes_time else 0) +
                        float(
                            unloading_time *
                            (
                                float(temp_capacity) +
                                float(capacity if capacity else 0)
                            )
                        )
                    )

                    if float(all_times_needed) < float(setting.minutes):
                        if isEnough:
                            check_tpa = TruckDirection.objects.filter(
                                mtrial_id=mtrial.pk,
                                truck_id=exist_truck.id
                            ).order_by('-id').first()

                            distance_to_tpa = tpa_dis.distance
                            amount_km = nearest.distance
                            takes_time = (
                                (float(loading_time) * float(rest)) +
                                float(nearest.distance) * velocity)

                            if check_tpa:
                                if check_tpa.place_id == ID_TPA:
                                    amount_km = distance_to_tpa
                                    takes_time = (
                                        float(amount_km * 2) +
                                        (
                                            float(rest if isEnough else gap) *
                                            loading_time
                                        )
                                    )

                            place_prob.update(rest=0 if isEnough else gap)
                            tr_direction = TruckDirection(
                                mtrial_id=mtrial.pk,
                                truck_id=exist_truck.id,
                                place_id=place_id,
                                takes_time=takes_time,
                                capacity=rest if isEnough else gap,
                                amount_km=amount_km,
                                emission=(
                                    (amount_km) *
                                    (fuel_factor.ems_factor) *
                                    (type_time.consumption)
                                )
                            )
                            tr_direction.save()

                            place_prob.update(status=StatusPlace.DONE)
                            complete_all = PlaceCompletement.objects.filter(
                                mtrial_id=mtrial.pk,
                                rest__gt=0).\
                                first()

                            if not complete_all:
                                truck.update(
                                    reach_minutes=time_total,
                                    is_complete=True
                                )

                            if place_id == ID_DIPO:
                                replace_tpa = {'to_place_id': place_id}
                            else:
                                replace_tpa = {'from_place_id': place_id}
                            ritation += 1

                        else:
                            takes_time = (float(distance_to_tpa) * velocity)
                            tr_tpa = TruckDirection(
                                mtrial_id=mtrial.pk,
                                truck_id=exist_truck.id,
                                place_id=ID_TPA,
                                takes_time=(
                                    takes_time + float(temp_capacity) *
                                    unloading_time
                                ),
                                capacity=float(temp_capacity),
                                amount_km=distance_to_tpa,
                                emission=(
                                    (distance_to_tpa) *
                                    (fuel_factor.ems_factor) *
                                    (type_time.consumption)
                                )
                            )
                            tr_tpa.save()

                            temp_capacity = 0
                            ritation = 1
                            replace_tpa = {'from_place_id': place_id}

                    else:
                        distance_to_tpa = tpa_dis.distance
                        takes_time = float(distance_to_tpa) * velocity

                        check_tpa = TruckDirection.objects.filter(
                            mtrial_id=mtrial.pk,
                            truck_id=exist_truck.id
                        ).order_by('-id').first()

                        if check_tpa.place_id is not ID_TPA:
                            tr_tpa = TruckDirection(
                                mtrial_id=mtrial.pk,
                                truck_id=exist_truck.id,
                                place_id=ID_TPA,
                                takes_time=(
                                    (float(unloading_time) * float(temp_capacity)) +
                                    float(distance_to_tpa) * velocity
                                ),
                                capacity=(
                                    float(temp_capacity) -
                                    (float(rest) if isEnough else 0)
                                ),
                                amount_km=distance_to_tpa,
                                emission=(
                                    (distance_to_tpa) *
                                    (fuel_factor.ems_factor) *
                                    (type_time.consumption)
                                )
                            )
                            tr_tpa.save()

                        tr_depot = TruckDirection(
                            mtrial_id=mtrial.pk,
                            truck_id=exist_truck.id,
                            place_id=ID_DIPO,
                            takes_time=float(depot_dis.distance) * velocity,
                            capacity=0,
                            amount_km=float(depot_dis.distance),
                            emission=(
                                float(depot_dis.distance) *
                                float(fuel_factor.ems_factor) *
                                float(type_time.consumption)
                            )
                        )
                        tr_depot.save()

                        sum_truck = TruckDirection.objects.filter(
                            mtrial_id=mtrial.pk,
                            truck_id=exist_truck.id
                        ).\
                            aggregate(
                                takes_time=Sum('takes_time'),
                        )

                        TruckHistory.objects.filter(
                            mtrial_id=mtrial.pk,
                            truck_id=truck_id
                        ).update(
                            reach_minutes=sum_truck['takes_time'],
                            is_complete=True,
                        )

                        temp_capacity = 0
                        all_times_needed = 0
                        ritation = 1
                        replace_tpa = None

                        truck_id += 1

        # return JsonResponse({
        #     'code': 200,
        #     'message': 'Success generate probability data!',
        # })
        return redirect("list_route_planning")

    @csrf_exempt
    @require_http_methods(["POST"])
    def get_truck_direction(request):
        mtrial_id = int(request.POST['mtrial_id'])
        truck_id = int(request.POST['truck_id'])

        print(f'mtrial_id : {mtrial_id}')
        print(f'truck_id : {truck_id}')

        history = TruckHistory.objects.get(pk=truck_id)
        direction = TruckDirection.objects.filter(
            mtrial_id=mtrial_id, truck_id=truck_id).all()

        trucks = [{
            **model_to_dict(dir),
            'type': dir.truck.type.truck_type,
            'cap': dir.truck.type.capacity,
            'truck': model_to_dict(dir.truck),
            'place': model_to_dict(dir.place)

        } for idx, dir in enumerate(direction)]

        return JsonResponse({
            'code': 200,
            'data': trucks
        })
