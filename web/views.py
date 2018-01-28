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
        line_codes = [line['line'][0] for line in Line.objects.values('line')]
        line_codes = sorted(list(set(line_codes)))
        return render(request, 'line_index.html', locals())
    else:
        data = Line.objects.get(line=line)
        line, arrive, start = data.line, data.start, data.arrive
        return render(request, 'line.html', locals())

def city(request, city):
    if city == 'index':
        citys = {}
        stations = [station['station'] for station in Timetable.objects.values('station').distinct()]
        for row in Station.objects.filter(cn__in=stations).values('cn', 'province', 'city', 'county'):
            cn, province, city, county = row['cn'], row['province'], row['city'], row['county']
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
    elif type == 'index_station':
        stations = [station['station'] for station in Timetable.objects.values('station').distinct()]
        stations = [station['cn'] for station in
                    Station.objects.filter(Q(cn__in=stations), Q(image_date__gt='1970-01-01')).values('cn')]
        data = random.sample(stations, 10)
    elif type == 'station_index':
        start, end = int(request.POST.get('start')), int(request.POST.get('end'))
        stations = Timetable.objects.values('station').annotate(count=Count('line')).order_by('-count')[start:end]
        count = {}
        for station in stations:
            count[station['station']] = station['count']
        stations = Station.objects.filter(cn__in=[station['station'] for station in stations]).values('cn', 'province',
                                                                                                      'city',
                                                                                                      'county')
        data = [[station['cn'], station['province'], station['city'], station['county']] for station in stations]
        data.sort(key=lambda x: count[x[0]], reverse=True)
    elif type == 'line_index':
        data = []
        code = request.POST.get('code')
        for line in Line.objects.filter(line__startswith=code).values('line', 'start', 'arrive'):
            data.append([line['line'], line['start'], line['arrive']])
        data = sorted(data, key=lambda x: int(x[0]) if x[0].isdigit() else int(x[0][1:]))
    elif type == 'station':
        name = request.POST.get('station')
        lines = [line.line for line in Timetable.objects.filter(station=name).order_by('leavetime')]
        timetable, stations1, stations2, stations_locations = {}, {}, {}, {}
        for row in Timetable.objects.filter(line__in=lines):
            line, order, station, arrivedate, arrivetime, leavedate, leavetime, staytime = row.line, row.order, row.station, row.arrivedate, str(
                row.arrivetime), row.leavedate, str(row.leavetime), row.staytime
            if station not in stations1:
                stations1[station] = {}
            stations1[station][line] = [order, arrivedate, arrivetime, leavedate, leavetime]
            if line not in timetable:
                timetable[line] = [None, None, None, None, None, 1]
            if order == 1:
                timetable[line][0] = station
                timetable[line][1] = station
            elif order > timetable[line][-1]:
                timetable[line][1] = station
                timetable[line][-1] = order
            if station == name:
                staytime = [staytime, '终', '始'][staytime if staytime in [-2, -1] else 0]
                timetable[line][2] = arrivetime
                timetable[line][3] = leavetime
                timetable[line][4] = staytime
        for station, station_data in stations1.items():
            if station != name:
                stations2[station] = [0, 10000]
                for line, line_data in station_data.items():
                    station_line = stations1[name][line]
                    a, b = [station_line, line_data] if line_data[0] < station_line[0] else [line_data, station_line]
                    runtime = round((datetime.strptime('1970010%s %s' % (a[1], a[2]),
                                                       '%Y%m%d %H:%M:%S') - datetime.strptime(
                        '1970010%s %s' % (b[3], b[4]), '%Y%m%d %H:%M:%S')).total_seconds() / 3600, 1)
                    if runtime < stations2[station][1]:
                        stations2[station][1] = runtime
                    stations2[station][0] += 1
        for info in Station.objects.filter(cn__in=[station for station in stations2] + [name]):
            stations_locations[info.cn] = [info.x, info.y, info.cn, info.province, info.city, info.county]
        timetable = sorted([[k] + v[:-1] for k, v in timetable.items()], key=lambda x: x[-2])
        stations = [stations_locations[k] + v for k, v in stations2.items()]
        stations.insert(0, stations_locations[name] + [0, 0])
        data = [timetable, stations]
    elif type == 'line':
        for row in Timetable.objects.filter(line=request.POST.get('line').upper()).order_by('order'):
            order, station, arrivedate, arrivetime, leavedate, leavetime, staytime = row.order, row.station, row.arrivedate, str(
                row.arrivetime), row.leavedate, str(row.leavetime), row.staytime
            staytime = [staytime, '终', '始'][staytime if staytime in [-2, -1] else 0]
            info = Station.objects.get(cn=station)
            data.append([info.x, info.y, info.province, info.city, info.county, order, station, arrivedate, arrivetime,
                         leavedate, leavetime, staytime])
    elif type == 'search':
        key = request.POST.get('key')
        data = [['station', '车站', []], ['city', '城市', []], ['line', '车次', []]]
        for row in Station.objects.filter(cn__contains=key).values('cn')[:10]:
            data[0][2].append(row['cn'])
        for row in Station.objects.filter(Q(province__contains=key) | Q(city__contains=key) | Q(county__contains=key))[
                   :10]:
            if key in row.county:
                row_data = row.province + '-' + row.city + '-' + row.county
            elif key in row.city:
                row_data = row.province + '-' + row.city
            else:
                row_data = row.province
            if row_data not in data[1][2]:
                data[1][2].append(row_data)
        for row in Line.objects.filter(line__contains=key.upper())[:20]:
            data[2][2].append(row.line)
        data = [[x, y, sorted(z)] for x, y, z in data if z != []]
    else:
        data = 'ERROR'
    return HttpResponse(json.dumps(data), content_type='application/json')


def log(request):
    return render(request, 'log.html')
