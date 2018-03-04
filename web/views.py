import json
import pickle
from datetime import *

from django.db.models import Count
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from redis import *

import key
from web.module import *

r = Redis(host='47.74.157.1', password=key.redis_pwd, port=6379, db=0)


def redis_data(func):
    def wrapper(name, *args):
        old = datetime.now().timestamp()
        data = r.get(name)
        if not data:
            data = func(*args)
            r.set(name, pickle.dumps(data))
            tomorrow = (datetime.now() + timedelta(days=1))
            r.expireat(name, int(datetime(tomorrow.year, tomorrow.month, tomorrow.day).timestamp() - 1))
        else:
            data = pickle.loads(data)
        print(name, datetime.now().timestamp() - old)
        return data

    return wrapper


def val(request):
    qiniu = 'http://qiniu.rail.qiangs.tech/station_img/'
    baidu_bak = key.baidu_bak
    amap_bak = key.amap_bak
    return locals()


def index(request):
    @redis_data
    def image_stations():
        line_stations = list(Timetable.objects.values_list('station', flat=True).distinct())
        return list(Station.objects.filter(Q(cn__in=line_stations), ~Q(image=None)).values_list('cn', flat=True))

    format = '.jpg?imageMogr2/auto-orient/thumbnail/x300/interlace/1/blur/1x0/quality/75|imageslim&time=%s' % str(
        datetime.now().date())
    stations = random.sample(image_stations('image_stations'), 10)
    return render(request, 'index.html', locals())


def station(request, station):
    @redis_data
    def get_count():
        return Timetable.objects.values('station').distinct().count()

    if station == 'index':
        format = '.jpg?imageMogr2/auto-orient/thumbnail/200x/interlace/1/blur/1x0/quality/75|imageslim&time=%s' % str(
            datetime.now().date())
        count = get_count('station_count')
        return render(request, 'station_index.html', locals())
    else:
        if Timetable.objects.filter(station=station):
            return render(request, 'station.html', locals())
        else:
            err = '%s站不存在或暂未开通客运服务' % station
            return render(request, '404.html', locals())


def line(request, line):
    @redis_data
    def get_line_codes():
        line_codes = list(Line.objects.values_list('line', flat=True))
        return sorted(list(set([line[0] for line in line_codes])))

    if line == 'index':
        line_codes = get_line_codes('line_codes')
        return render(request, 'line_index.html', locals())
    else:
        if Timetable.objects.filter(line=line.upper()):
            return render(request, 'line.html', locals())
        else:
            err = '%s次不存在或无详细时刻信息' % line
            return render(request, '404.html', locals())


def city(request, city):
    return render(request, 'city.html', locals())


def data(request):
    def log():
        with open('get_data/data.log', 'r') as f:
            logs = f.read()
        return [log.split('-|-')[1:] for log in logs.split('||') if 'ERROR' in log and '-|-' in log][-100:][::-1]

    def station_index(start, end):
        sort_stations = list(
            Timetable.objects.values('station').annotate(
                count=Count('line')).order_by('-count')[int(start):int(end)].values_list('station', flat=True))
        stations = list(Station.objects.filter(cn__in=sort_stations).values_list('cn', 'province', 'city', 'county'))
        return sorted(stations, key=lambda x: sort_stations.index(x[0]))

    def line_index(code):
        data = [line for line in
                Line.objects.filter(Q(line__startswith=code), ~Q(runtime=None)).values_list('line', 'start',
                                                                                            'arrive')]
        return sorted(data, key=lambda x: (x[0][0], int(x[0].split('/')[0][1:]) if len(x[0]) > 1 else 0))

    def city():
        data = {}
        stations = list(Timetable.objects.values_list('station', flat=True).distinct())
        for item in Station.objects.filter(cn__in=stations).values_list('cn', 'province', 'city', 'county'):
            cn, province, city, county = item
            if province not in data:
                data[province] = {}
            if city not in data[province]:
                data[province][city] = {}
            if county in data[province][city]:
                data[province][city][county].append(cn)
            else:
                data[province][city][county] = [cn]
        return data

    def station(station):
        lines = list(Timetable.objects.filter(station=station).order_by('leavetime').values_list('line', flat=True))
        timetable, stations_line, stations_data, stations_locations = {}, {}, {}, {}
        for item in Timetable.objects.filter(line__in=lines).values_list('line', 'station', 'order', 'arrivedate',
                                                                         'arrivetime', 'leavedate', 'leavetime',
                                                                         'staytime'):
            line, cn, order, arrivedate, arrivetime, leavedate, leavetime, staytime = item
            if cn not in stations_line:
                stations_line[cn] = {}
            stations_line[cn][line] = item[2:]
            if line not in timetable:
                timetable[line] = [None, None, None, None, None, 1]
            if order == 1:
                timetable[line][:2] = [cn, cn]
            elif order > timetable[line][-1]:
                timetable[line][1] = cn
                timetable[line][-1] = order
            if cn == station:
                timetable[line][2:5] = [str(arrivetime)[:-3], str(leavetime)[:-3], staytime]
        for cn, station_data in stations_line.items():
            if cn != station:
                stations_data[cn] = [0, 10000]
                for line, line_data in station_data.items():
                    station_line = stations_line[station][line]
                    a, b = [station_line, line_data] if line_data[0] < station_line[0] else [line_data, station_line]
                    runtime = round((datetime(1970, 1, a[1], a[2].hour, a[2].minute, 0) - datetime(1970, 1, b[3],
                                                                                                   b[4].hour,
                                                                                                   b[4].minute,
                                                                                                   0)).total_seconds() / 3600,
                                    1)
                    if runtime < stations_data[cn][1]:
                        stations_data[cn][1] = runtime
                    stations_data[cn][0] += 1
        for item in Station.objects.filter(cn__in=[cn for cn in stations_data] + [station]).values_list('x', 'y',
                                                                                                        'cn',
                                                                                                        'province',
                                                                                                        'city',
                                                                                                        'county'):
            stations_locations[item[2]] = list(item)
        timetable = sorted([[k] + v[:-1] for k, v in timetable.items()], key=lambda x: x[-2])
        stations = [stations_locations[k] + v for k, v in stations_data.items()]
        stations.insert(0, stations_locations[station] + [0, 0])
        return {'lines': timetable, 'stations': stations,
                'info': Station.objects.filter(cn=station).values_list('province', 'city', 'county')[0]}

    def line(line):
        lines, stations = [], []
        for item in Timetable.objects.filter(line=line).order_by('order').values_list('order', 'station', 'arrivedate',
                                                                                      'arrivetime', 'leavedate',
                                                                                      'leavetime',
                                                                                      'staytime'):
            item, item[3], item[5] = list(item), str(item[3])[:-3], str(item[5])[:-3]
            lines.append(item)
            stations.append(item[1])
        for item in Station.objects.filter(cn__in=stations).values_list('cn', 'x', 'y', 'province', 'city', 'county'):
            n = stations.index(item[0])
            lines[n] = list(item[1:]) + lines[n]
        return {'lines': lines, 'info': list(Line.objects.filter(line=line).values_list('start', 'arrive'))[0]}

    def err():
        return 'ERROR'

    def index_china():
        lines = list(Line.objects.values('start', 'arrive').values_list('start', 'arrive').distinct())
        cns = []
        for line in lines:
            cns += line[:2]
        stations = list(Station.objects.filter(cn__in=set(cns)).values_list('cn', 'x', 'y'))
        index = {}
        for n in range(len(stations)):
            index[stations[n][0]] = n
        lines = [[index[line[0]], index[line[1]]] for line in lines]
        return {'stations': [station[1:] for station in stations], 'lines': lines}

    @redis_data
    def main(post):
        type = post.pop('type', '')
        methods = {'log': log, 'index_china': index_china, 'station_index': station_index, 'line_index': line_index,
                   'city': city, 'station': station,
                   'line': line, 'search': search, 'luck': luck}
        return methods.get(type, err)(**post)

    post = dict(request.POST.items())
    post.pop('csrfmiddlewaretoken')
    data = main('__'.join(sorted(post.values())), post)
    return HttpResponse(json.dumps(data), content_type='application/json')


def log(request):
    return render(request, 'log.html')
