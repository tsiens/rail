from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from get_data.get_ticket import get_ticket
import json, random
from datetime import datetime
from web.models import *
from django.db.models import Q
from pypinyin import lazy_pinyin

sort_pinyin = lambda keys: sorted(keys, key=lambda x: ''.join([i[0] for i in lazy_pinyin(x[0][:2])]))

qiniu = 'http://qiniu.rail.qiangs.tech/'
img = '.jpg?imageMogr2/thumbnail/x480/format/webp/blur/1x0/quality/75|imageslim'
def index(request):
    last = Station.objects.count()
    images = []
    while len(images) < 10:
        station = Station.objects.all()[random.randint(0, last)]
        if station.image_date and Timetable.objects.filter(station=station.cn):
            images.append(station.cn)
    return render(request, 'index.html', {'images': images, 'qiniu': qiniu, 'img': img})

def log(request):
    return render(request, 'log.html')


def station(request, station):
    data = Station.objects.get(cn=station)
    return render(request, 'station.html',
                  {'station': station, 'province': data.province, 'city': data.city, 'county': data.county})
def line(request, line):
    data = Line.objects.get(line=line)
    return render(request, 'line.html', {'line': line, 'start': data.start, 'arrive': data.arrive})


def city(request):
    data = {}
    stations = [station['station'] for station in Timetable.objects.all().values('station').distinct()]
    for row in Station.objects.filter(cn__in=stations).values('cn', 'province', 'city', 'county'):
        cn, province, city, county = row['cn'], row['province'], row['city'], row['county']
        if 'None' in [province, city, county] or None in [province, city, county]:
            print(cn)
        if province not in data:
            data[province] = {}
        if city not in data[province]:
            data[province][city] = {}
        if county in data[province][city]:
            data[province][city][county].append(cn)
        else:
            data[province][city][county] = [cn]
    province_list = []
    for province, citys in data.items():
        city_list = []
        for city, countys in citys.items():
            county_list = []
            for county, cns in countys.items():
                cns_list = [cn for cn in cns]
                county_list.append([county, sort_pinyin(cns_list)])
            city_list.append([city, sort_pinyin(county_list)])
        province_list.append([province, sort_pinyin(city_list)])
    return render(request, 'city.html',
                  {'citys': sort_pinyin(province_list), 'ids': ['province', 'city', 'county', 'station', 'href']})

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
        for row in Station.objects.filter(cn__contains=key).values('cn'):
            data[0][2].append(row['cn'])
        for row in Station.objects.filter(Q(province__contains=key) | Q(city__contains=key) | Q(county__contains=key)):
            if key in row.county:
                row_data = row.province + '-' + row.city + '-' + row.county
            elif key in row.city:
                row_data = row.province + '-' + row.city
            else:
                row_data = row.province
            if row_data not in data[1][2]:
                data[1][2].append(row_data)
        for row in Line.objects.filter(line__contains=key)[:10]:
            data[2][2].append(row.line)
        data = [[x, y, sorted(z)] for x, y, z in data if z != []]
    else:
        data = 'ERROR'
    return HttpResponse(json.dumps(data), content_type='application/json')
