from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from django.forms import model_to_dict
from django.db.models import Sum
from django.http.response import JsonResponse
from django.db.models import Q
from django.shortcuts import redirect, render

from master.models import *
from transaction.controller.ExportController import render_to_pdf
from transaction.models import *
from django.db.models import Min

from django.contrib import messages


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
                      "route-planning/index.html",
                      {
                          'title': 'Route Planning',
                          "rp": rp,
                      })

    def create(request):
        velocity = SettingWork.objects.all().first()
        fuel = Fuel.objects.all()
        armroll = TypeTime.objects.get(type_id=1)
        dump = TypeTime.objects.get(type_id=2)

        return render(request,
                      "route-planning/add.html",
                      {
                          'title': 'Add Route Planning',
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
                      "route-planning/edit.html",
                      {
                          'title': 'Detail Route Planning',
                          'c_distance': total_distance,
                          'c_emission': total_emision,
                          'c_exist_truck': c_exist_truck,
                          'c_truck': c_truck,
                          'main': main,
                          "fuel": fuel,
                          'truck_history': truck_history
                      })

    def complete_step(
        **kwargs
    ):
        distance_to_tpa = kwargs['tpa_dis'].distance
        takes_time = float(distance_to_tpa) * kwargs['velocity']

        check_tpa = TruckDirection.objects.filter(
            mtrial_id=kwargs['mtrial'].pk,
            truck_id=kwargs['exist_truck'].id
        ).order_by('-id').first()

        if check_tpa.place_id is not kwargs['ID_TPA']:
            tr_tpa = TruckDirection(
                mtrial_id=kwargs['mtrial'].pk,
                truck_id=kwargs['exist_truck'].id,
                place_id=kwargs['ID_TPA'],
                takes_time=(
                    (float(kwargs['unloading_time']) * float(kwargs['temp_capacity'])) +
                    float(distance_to_tpa) * kwargs['velocity']
                ),
                capacity=(
                    float(kwargs['temp_capacity']) -
                    (float(kwargs['rest']) if kwargs['isEnough'] else 0)
                ),
                amount_km=distance_to_tpa,
                emission=(
                    (distance_to_tpa) *
                    (kwargs['fuel_factor'].ems_factor) *
                    (kwargs['type_time'].consumption)
                )
            )
            tr_tpa.save()

        tr_depot = TruckDirection(
            mtrial_id=kwargs['mtrial'].pk,
            truck_id=kwargs['exist_truck'].id,
            place_id=kwargs['ID_DIPO'],
            takes_time=float(
                kwargs['depot_dis'].distance) * kwargs['velocity'],
            capacity=0,
            amount_km=float(kwargs['depot_dis'].distance),
            emission=(
                float(kwargs['depot_dis'].distance) *
                float(kwargs['fuel_factor'].ems_factor) *
                float(kwargs['type_time'].consumption)
            )
        )
        tr_depot.save()

        sum_truck = TruckDirection.objects.filter(
            mtrial_id=kwargs['mtrial'].pk,
            truck_id=kwargs['exist_truck'].id
        ).\
            aggregate(
                takes_time=Sum('takes_time'),
        )

        TruckHistory.objects.filter(
            mtrial_id=kwargs['mtrial'].pk,
            truck_id=kwargs['truck_id']
        ).update(
            reach_minutes=sum_truck['takes_time'],
            is_complete=True,
        )

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
            velocity=float(q_velocity),
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
                break

            if truck_type is int(TruckType.ARMROLL.value):
                is_dump = PlaceCompletement.objects.filter(mtrial_id=mtrial.pk).\
                    filter(Q(status=StatusPlace.YET)).count()
                if is_dump < 1:
                    truck_type = int(TruckType.DUMP.value)
                    truck_capacity = Capacity.DUMP.value
                    ritation = 1

            nearest = None
            params = (
                {'to_place_id': dipo.id} if ritation == 1 else
                {'from_place_id': tpa.id}
            )

            if replace_tpa:
                params = replace_tpa

            prob_nearest = PlaceDistance.objects.filter(**params).\
                annotate(Min("distance")).\
                order_by('distance')

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

                    if exist_truck:
                        time_total = float(exist_truck.reach_minutes) + \
                            time_journey +\
                            (float(depot_dis.distance) * velocity) + (float(nearest.distance) *
                                                                      velocity)

                        if float(time_total) < float(setting.minutes):
                            if rest >= float(truck_capacity):
                                truck.update(
                                    reach_minutes=time_total - (float(depot_dis.distance) * velocity))

                                up_rest = float(rest) - float(truck_capacity)
                                place_prob.update(rest=up_rest)

                                if up_rest < truck_capacity:
                                    place_prob.update(
                                        status=StatusPlace.PARTIAL.value)

                                if up_rest <= 0:
                                    place_prob.update(
                                        status=StatusPlace.DONE.value)

                                dctn = TruckDirection(
                                    mtrial_id=mtrial.pk,
                                    truck_id=exist_truck.id,
                                    place_id=place_id,
                                    takes_time=(
                                        time_total -
                                        (float(depot_dis.distance) * velocity)
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
                                place_prob.update(
                                    status=StatusPlace.PARTIAL.value)
                                ritation += 1

                        else:
                            dctn = TruckDirection(
                                mtrial_id=mtrial.pk,
                                truck_id=exist_truck.id,
                                place_id=2,
                                takes_time=0,
                                capacity=0,
                                amount_km=depot_dis.distance,
                                emission=(
                                    (depot_dis.distance) *
                                    (fuel_factor.ems_factor) *
                                    (type_time.consumption)
                                )
                            )
                            dctn.save()

                            truck.update(
                                is_complete=True,
                                reach_minutes=(
                                    float(exist_truck.reach_minutes) +
                                    (float(depot_dis.distance) * velocity)
                                )
                            )
                            ritation = 1
                            truck_id += 1

                    else:
                        tps_to_tpa = PlaceDistance.objects.filter(
                            from_place_id=tpa.id,
                            to_place_id=place_id,
                        ).first()

                        # Check if restunder capacity of armroll
                        up_rest = float(rest) - float(truck_capacity)
                        place_prob.update(rest=up_rest)
                        if up_rest < truck_capacity:
                            place_prob.update(
                                status=StatusPlace.PARTIAL.value)

                        if up_rest <= 0:
                            place_prob.update(
                                status=StatusPlace.DONE.value)

                        truck = TruckHistory(
                            mtrial_id=mtrial.pk,
                            type_id=truck_type,
                            truck_id=truck_id,
                            reach_minutes=time_journey +
                            (float(tps_to_tpa.distance) * velocity),
                        )
                        truck.save()

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

                # TRUCK DUMP
                elif truck_type is int(TruckType.DUMP.value):
                    loading_time = float(
                        q_loading_dump) if q_loading_dump else type_time.loading_time
                    unloading_time = float(
                        q_unloading_dump) if q_unloading_dump else type_time.unloading_time

                    gap = float(truck_capacity) - float(temp_capacity)
                    isEnough = rest <= gap

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

                            if is_finish <= 1:
                                RoutePlanningController.complete_step(
                                    ID_TPA=ID_TPA,
                                    ID_DIPO=ID_DIPO,
                                    tpa_dis=tpa_dis,
                                    velocity=velocity,
                                    mtrial=mtrial,
                                    exist_truck=exist_truck,
                                    unloading_time=unloading_time,
                                    temp_capacity=temp_capacity,
                                    rest=rest,
                                    isEnough=isEnough,
                                    fuel_factor=fuel_factor,
                                    type_time=type_time,
                                    depot_dis=depot_dis,
                                    truck_id=truck_id,
                                )

                                temp_capacity = 0
                                all_times_needed = 0
                                ritation = 1
                                replace_tpa = None

                                truck_id += 1

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
                        RoutePlanningController.complete_step(
                            ID_TPA=ID_TPA,
                            ID_DIPO=ID_DIPO,
                            tpa_dis=tpa_dis,
                            velocity=velocity,
                            mtrial=mtrial,
                            exist_truck=exist_truck,
                            unloading_time=unloading_time,
                            temp_capacity=temp_capacity,
                            rest=rest,
                            isEnough=isEnough,
                            fuel_factor=fuel_factor,
                            type_time=type_time,
                            depot_dis=depot_dis,
                            truck_id=truck_id,
                        )

                        temp_capacity = 0
                        all_times_needed = 0
                        ritation = 1
                        replace_tpa = None

                        truck_id += 1

        messages.success(request, "Success generate route planning!")
        return redirect("list_route_planning")

    @csrf_exempt
    @require_http_methods(["POST"])
    def get_truck_direction(request):
        mtrial_id = int(request.POST['mtrial_id'])
        truck_id = int(request.POST['truck_id'])

        history = TruckHistory.objects.get(pk=truck_id)
        direction = TruckDirection.objects.filter(
            mtrial_id=mtrial_id, truck_id=truck_id).order_by('id').all()

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

    @csrf_exempt
    @require_http_methods(["GET"])
    def export_recap(request, id):
        directions = ['']
        amount_kms = ['']
        emissions = ['']

        reach_minutes = 0
        reach_kms = 0
        reach_emission = 0

        planning = MainTrial.objects.get(pk=id)
        th = TruckHistory.objects.filter(
            mtrial_id=id)
        truck_history = th.order_by('id')

        for truck in truck_history:
            reach_minutes += truck.reach_minutes

            direction = TruckDirection.objects.filter(
                truck_id=truck.id).order_by('id')
            temp_dir = ''
            temp_km = 0
            temp_ems = 0

            for idx, dir in enumerate(direction):
                reach_kms += dir.amount_km
                reach_emission += dir.emission

                if idx is 0:
                    temp_dir += '0 - '

                temp_dir += (dir.place.nodes)
                temp_km += (dir.amount_km)
                temp_ems += (dir.emission)

                if idx != len(direction) - 1:
                    temp_dir += ' - '

                if (idx != len(direction) - 1) and (truck.type_id == 1):
                    temp_dir += 'X - '

            directions.append(temp_dir)
            amount_kms.append(temp_km)
            emissions.append(temp_ems)

        pdf = render_to_pdf('print/table-recap.html', {
            'name': planning.name,
            'truck_history': truck_history,
            'directions': directions,
            'amount_kms': amount_kms,
            'emissions': emissions,
            'amount_truck': len(truck_history),
            'amount_armroll': len(th.filter(type_id=1)),
            'amount_dump': len(th.filter(type_id=2)),
            'amount_minutes': reach_minutes,
            'amount_km': reach_kms,
            'amount_emission': reach_emission,
        })

        return HttpResponse(pdf, content_type='application/pdf')

    @csrf_exempt
    @require_http_methods(["POST"])
    def delete(request):
        id = int(request.POST['id'])
        TruckDirection.objects.filter().delete()
        TruckHistory.objects.filter().delete()
        PlaceCompletement.objects.filter().delete()
        MainTrial.objects.filter().delete()

        messages.success(request, "Success delete route planning!")
        return redirect("list_route_planning")
