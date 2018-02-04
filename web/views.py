import json
import random
from datetime import datetime

from django.db.models import Q, Count
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

import key
from web.models import *


def val(request):
    qiniu = 'http://qiniu.rail.qiangs.tech/station_img/'
    baidu_bak = key.baidu_bak
    amap_bak = key.amap_bak
    return locals()


def index(request):
    format = '.jpg?imageMogr2/auto-orient/thumbnail/x300/interlace/1/blur/1x0/quality/75|imageslim'
    line_stations = list(Timetable.objects.values_list('station', flat=True).distinct())
    image_stations = list(Station.objects.filter(Q(cn__in=line_stations), ~Q(image=None)).values_list('cn', flat=True))
    stations = random.sample(image_stations, 10)
    return render(request, 'index.html', locals())


def station(request, station):
    if station == 'index':
        format = '.jpg?imageMogr2/auto-orient/thumbnail/200x/interlace/1/blur/1x0/quality/75|imageslim'
        count = Timetable.objects.values('station').distinct().count()
        return render(request, 'station_index.html', locals())
    else:
        data = Station.objects.get(cn=station)
        return render(request, 'station.html', locals())


def line(request, line):
    if line == 'index':
        line_codes = list(Line.objects.values_list('line', flat=True))
        line_codes = sorted(list(set([line[0] for line in line_codes])))
        return render(request, 'line_index.html', locals())
    else:
        data = Line.objects.get(line=line)
        line, arrive, start = data.line, data.start, data.arrive
        return render(request, 'line.html', locals())


def city(request, city):
    if city == 'index':
        citys = {}
        stations = list(Timetable.objects.values_list('station', flat=True).distinct())
        for item in Station.objects.filter(cn__in=stations).values_list('cn', 'province', 'city', 'county'):
            cn, province, city, county = item
            if province not in citys:
                citys[province] = {}
            if city not in citys[province]:
                citys[province][city] = {}
            if county in citys[province][city]:
                citys[province][city][county].append(cn)
            else:
                citys[province][city][county] = [cn]
        return render(request, 'city.html', locals())


def data(request):
    type = request.POST.get('type')
    data = []
    if type == 'log':
        with open('get_data/data.log', 'r') as f:
            logs = f.read()
        data = [log.split('-|-')[1:] for log in logs.split('||') if 'ERROR' in log and '-|-' in log][-100:][::-1]
    elif type == 'station_index':
        start, end = int(request.POST.get('start')), int(request.POST.get('end'))
        image_stations = list(Station.objects.exclude(image=None).values_list('cn', flat=True))
        line_stations = list(Timetable.objects.values_list('station', flat=True).distinct())
        sort_stations = list(
            Timetable.objects.filter(station__in=image_stations + line_stations).values('station').annotate(
                count=Count('line')).order_by('-count')[start:end].values_list('station', flat=True))
        stations = list(Station.objects.filter(cn__in=sort_stations).values_list('cn', 'province', 'city', 'county'))
        data = sorted(stations, key=lambda x: sort_stations.index(x[0]))
    elif type == 'line_index':
        data = []
        code = request.POST.get('code')
        for line in Line.objects.filter(Q(line__startswith=code), ~Q(runtime=None)).values_list('line', 'start',
                                                                                                'arrive'):
            data.append(line)
        data = sorted(data, key=lambda x: (x[0][0], int(x[0][1:]) if len(x[0]) > 1 else 0))
    elif type == 'station':
        name = request.POST.get('station')
        lines = list(Timetable.objects.filter(station=name).order_by('leavetime').values_list('line', flat=True))
        timetable, stations_line, stations_data, stations_locations = {}, {}, {}, {}
        for item in Timetable.objects.filter(line__in=lines).values_list('line', 'station', 'order', 'arrivedate',
                                                                         'arrivetime', 'leavedate', 'leavetime',
                                                                         'staytime'):
            line, station, order, arrivedate, arrivetime, leavedate, leavetime, staytime = item
            if station not in stations_line:
                stations_line[station] = {}
            stations_line[station][line] = item[2:]
            if line not in timetable:
                timetable[line] = [None, None, None, None, None, 1]
            if order == 1:
                timetable[line][:2] = [station, station]
            elif order > timetable[line][-1]:
                timetable[line][1] = station
                timetable[line][-1] = order
            if station == name:
                timetable[line][2:5] = [str(arrivetime), str(leavetime), staytime]
        for station, station_data in stations_line.items():
            if station != name:
                stations_data[station] = [0, 10000]
                for line, line_data in station_data.items():
                    station_line = stations_line[name][line]
                    a, b = [station_line, line_data] if line_data[0] < station_line[0] else [line_data, station_line]
                    runtime = round((datetime(1970, 1, a[1], a[2].hour, a[2].minute, 0) - datetime(1970, 1, b[3],
                                                                                                   b[4].hour,
                                                                                                   b[4].minute,
                                                                                                   0)).total_seconds() / 3600,
                                    1)
                    if runtime < stations_data[station][1]:
                        stations_data[station][1] = runtime
                    stations_data[station][0] += 1
        for item in Station.objects.filter(cn__in=[station for station in stations_data] + [name]).values_list('x', 'y',
                                                                                                               'cn',
                                                                                                               'province',
                                                                                                               'city',
                                                                                                               'county'):
            stations_locations[item[2]] = list(item)
        timetable = sorted([[k] + v[:-1] for k, v in timetable.items()], key=lambda x: x[-2])
        stations = [stations_locations[k] + v for k, v in stations_data.items()]
        stations.insert(0, stations_locations[name] + [0, 0])
        data = [timetable, stations]
    elif type == 'line':
        name = request.POST.get('line').upper()
        stations = []
        for item in Timetable.objects.filter(line=name).order_by('order').values_list('order', 'station', 'arrivedate',
                                                                                      'arrivetime', 'leavedate',
                                                                                      'leavetime',
                                                                                      'staytime'):
            data.append([str(i) for i in item])
            stations.append(item[1])
        for item in Station.objects.filter(cn__in=stations).values_list('cn', 'x', 'y', 'province', 'city', 'county'):
            n = stations.index(item[0])
            data[n] = list(item[1:]) + data[n]
    elif type == 'search':
        key = request.POST.get('key').upper()
        data = {'车站': [], '城市': [], '车次': []}
        for item in Station.objects.filter(Q(province__contains=key) | Q(city__contains=key) | Q(county__contains=key))[
                    :10].values_list('province', 'city', 'county'):
            province, city, county = item
            if key in county:
                item_data = province + '-' + city + '-' + county
            elif key in city:
                item_data = province + '-' + city
            else:
                item_data = province
            if item_data not in data['城市']:
                data['城市'].append(item_data)
        line_stations = list(Timetable.objects.values_list('station', flat=True).distinct())
        data['车站'] = sorted([item for item in
                             Station.objects.filter(Q(cn__contains=key), Q(cn__in=line_stations)).values_list('cn',
                                                                                                              flat=True)[
                             :10]])
        data['车次'] = sorted([item for item in
                             Line.objects.filter(Q(line__contains=key), ~Q(runtime=None)).values_list('line',
                                                                                                      flat=True)[:10]],
                            key=lambda x: (x[0], int(x[1:]) if len(x) > 1 else 0))
        data['城市'] = sorted(data['城市'])
    else:
        data = 'ERROR'
    return HttpResponse(json.dumps(data), content_type='application/json')


def log(request):
    return render(request, 'log.html')
