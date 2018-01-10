from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from get_data.get_ticket import get_ticket
import json, random
from datetime import datetime
from web.models import *

qiniu = 'http://qiniu.rail.qiangs.tech'
def index(request):
    last = Station.objects.count()
    station = Station.objects.all()[random.randint(0, last)]
    if station.image_date and Timetable.objects.filter(station=station.cn):
        return render(request, 'index.html', {'cn': station.cn, 'qiniu': qiniu})
    else:
        return index(request)

def log(request):
    return render(request, 'log.html')
def station(request, cn):
    data = Station.objects.get(cn=cn)
    return render(request, 'station.html',
                  {'station': cn, 'province': data.province, 'city': data.city, 'county': data.county})


def line(request, line):
    data = Line.objects.get(line=line)
    return render(request, 'line.html', {'line': line, 'start': data.start, 'arrive': data.arrive})


def ticket(request, start, arrive, date):
    if len(date) < 3:
        year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        date = str(datetime(year, month + 1 if int(date) < day else month, int(date)).date())
    return render(request, 'ticket.html', {'start': start, 'arrive': arrive, 'date': date})


def data(request):
    type = request.POST.get('type', 'error')
    if type == 'log':
        with open('get_data/data.log', 'r') as f:
            logs = f.read()
        data = [log.split('-|-')[1:] for log in logs.split('||') if 'ERROR' in log and '-|-' in log][-100:][::-1]
    elif type == 'station':
        data = []
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
        data = []
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
    else:
        data = get_ticket(*request.POST.get('info').split('|'))
    return HttpResponse(json.dumps(data), content_type='application/json')
