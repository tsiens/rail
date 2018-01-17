from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from get_data.get_ticket import get_ticket
import json, random
from datetime import datetime
from web.models import *
from django.db.models import Q, Count


def val(request):
    qiniu = 'http://qiniu.rail.qiangs.tech/station_img/'
    level = ['province', 'city', 'county', 'station']
    nav = {'header': [{'rel': True, 'href': 'https://github.com/tsiens/rail', 'fa': 'fa-github', 'text': ''},
                      {'href': '/', 'text': 'Rail'},
                      {'href': '/', 'fa': 'fa-home', 'text': '主页'},
                      {'href': '/ticket/杭州/上海/16', 'fa': 'fa-ticket', 'text': '余票'},
                      {'href': '/station/index', 'fa': 'fa-train', 'text': '车站'},
                      {'href': '/line/Z258', 'fa': 'fa-list-alt', 'text': '车次'},
                      {'href': '/city', 'fa': 'fa-map-o', 'text': '城市'},
                      {'target': '#modal_wechat', 'fa': 'fa-wechat', 'text': '公众号'},
                      {'target': '#modal_contact', 'fa': 'fa-user', 'text': '交流'},
                      {'target': '#modal_search', 'fa': 'fa-search', 'text': 'search'},
                      ],
           'modal': [{'id': 'modal_wechat', 'fa': 'wechat', 'text': '12308', 'src': 'image/wechat.jpg'},
                     {'id': 'modal_contact', 'fa': 'fa-user"', 'text': '吐槽我吧', 'src': 'image/qq.jpg'},
                     {'id': 'modal_search', 'fa': 'search"', 'text': 'search'}], }
    return {'level': level, 'nav': nav, 'qiniu': qiniu}

def index(request):
    format = '.jpg?imageMogr2/auto-orient/thumbnail/x300/interlace/1/blur/1x0/quality/75|imageslim'
    stations = [station['station'] for station in Timetable.objects.all().values('station').distinct()]
    stations = [station['cn'] for station in Station.objects.filter(cn__in=stations).values('cn')]
    stations = random.sample(stations, 10)
    return render(request, 'index.html', {'stations': stations, 'format': format})

def log(request):
    return render(request, 'log.html')

def station(request, station):
    if station == 'index':
        format = '.jpg?imageMogr2/auto-orient/thumbnail/200x/interlace/1/blur/1x0/quality/75|imageslim'
        stations = Timetable.objects.values('station').annotate(dcount=Count('line'))
        count = {}
        for station in stations:
            count[station['station']] = station['dcount']
        stations = list(
            Station.objects.filter(cn__in=[station['station'] for station in stations]).values('cn', 'province', 'city',
                                                                                               'county'))
        stations.sort(key=lambda x: count[x['cn']], reverse=True)
        return render(request, 'station_index.html', {'stations': stations, 'format': format})
    else:
        data = Station.objects.get(cn=station)
        return render(request, 'station.html',
                      {'station': station, 'province': data.province, 'city': data.city,
                       'county': data.county})
def line(request, line):
    data = Line.objects.get(line=line)
    return render(request, 'line.html', {'line': line, 'start': data.start, 'arrive': data.arrive})


def city(request):
    data = {}
    stations = [station['station'] for station in Timetable.objects.all().values('station').distinct()]
    for row in Station.objects.filter(cn__in=stations).values('cn', 'province', 'city', 'county'):
        cn, province, city, county = row['cn'], row['province'], row['city'], row['county']
        if province not in data:
            data[province] = {}
        if city not in data[province]:
            data[province][city] = {}
        if county in data[province][city]:
            data[province][city][county].append(cn)
        else:
            data[province][city][county] = [cn]
    return render(request, 'city.html', {'citys': data})

def ticket(request, start, arrive, date):
    if len(date) < 3:
        year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        date = str(datetime(year, month + 1 if int(date) < day else month, int(date)).date())
    return render(request, 'ticket.html', {'start': start, 'arrive': arrive, 'date': date})


def data(request):
    type = request.POST.get('type')
    data = []
    if type == 'log':
        with open('get_data/data.log', 'r') as f:
            logs = f.read()
        data = [log.split('-|-')[1:] for log in logs.split('||') if 'ERROR' in log and '-|-' in log][-100:][::-1]
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
    elif type == 'ticket':
        data = get_ticket(*request.POST.get('info').split('|'))
    elif type == 'search':
        key = request.POST.get('key')
        data = [['station', '车站', []], ['city', '城市', []], ['line', '车次', []]]
        for row in Station.objects.filter(cn__contains=key).values('cn')[:5]:
            data[0][2].append(row['cn'])
        for row in Station.objects.filter(Q(province__contains=key) | Q(city__contains=key) | Q(county__contains=key))[
                   :5]:
            if key in row.county:
                row_data = row.province + '-' + row.city + '-' + row.county
            elif key in row.city:
                row_data = row.province + '-' + row.city
            else:
                row_data = row.province
            if row_data not in data[1][2]:
                data[1][2].append(row_data)
        for row in Line.objects.filter(line__contains=key)[:5]:
            data[2][2].append(row.line)
        data = [[x, y, sorted(z)] for x, y, z in data if z != []]
    else:
        data = 'ERROR'
    return HttpResponse(json.dumps(data), content_type='application/json')
