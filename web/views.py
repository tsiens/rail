from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import json, random
from web.models import *
from django.db.models import Q, Count


def val(request):
    qiniu = 'http://qiniu.rail.qiangs.tech/station_img/'
    level = ['province', 'city', 'county', 'station']
    nav = {'header': [{'type': 0, 'rel': True, 'href': 'https://github.com/tsiens/rail', 'fa': 'fa-github', 'text': ''},
                      {'type': 0, 'href': '/', 'text': 'Rail'},
                      {'type': 1, 'href': '/', 'fa': 'fa-home', 'text': '主页'},
                      {'type': 1, 'href': '/station/index', 'fa': 'fa-train', 'text': '车站'},
                      {'type': 1, 'href': '/line/index', 'fa': 'fa-list-alt', 'text': '车次'},
                      {'type': 1, 'href': '/city/index', 'fa': 'fa-map-o', 'text': '城市'},
                      {'type': 2, 'target': '#modal_wechat', 'fa': 'fa-wechat', 'text': '公众号'},
                      {'type': 2, 'target': '#modal_contact', 'fa': 'fa-user', 'text': '交流'},
                      {'type': 2, 'target': '#modal_search', 'fa': 'fa-search', 'text': 'search'},
                      ],
           'modal': [{'id': 'modal_wechat', 'fa': 'wechat', 'text': '12308', 'src': 'image/wechat.jpg'},
                     {'id': 'modal_contact', 'fa': 'fa-user"', 'text': '吐槽我吧', 'src': 'image/qq.jpg'},
                     {'id': 'modal_search', 'fa': 'search"', 'text': 'search'}], }
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
        stations = [station['cn'] for station in Station.objects.filter(cn__in=stations).values('cn')]
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
        for row in Timetable.objects.filter(station=request.POST.get('station')).order_by('leavetime'):
            line, arrivetime, leavetime, staytime = row.line, str(row.arrivetime), str(row.leavetime), row.staytime
            line_data = Line.objects.get(line=line)
            start = line_data.start
            arrive = line_data.arrive
            staytime = [staytime, '终', '始'][staytime if staytime in [-2, -1] else 0]
            if staytime == '始': arrivetime = '-' * 11
            if staytime == '终': leavetime = '-' * 11
            data.append([line, start, arrive, arrivetime, leavetime, staytime])
    elif type == 'line':
        for row in Timetable.objects.filter(line=request.POST.get('line').upper()).order_by('order'):
            order, station, arrivedate, arrivetime, leavedate, leavetime, staytime = row.order, row.station, row.arrivedate, str(
                row.arrivetime), row.leavedate, str(row.leavetime), row.staytime
            staytime = [staytime, '终', '始'][staytime if staytime in [-2, -1] else 0]
            if staytime == '始':
                arrivedate = '--'
                arrivetime = '-' * 11
            if staytime == '终':
                leavedate = '--'
                leavetime = '-' * 11
            data.append([order, station, arrivedate, arrivetime, leavedate, leavetime, staytime])
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
