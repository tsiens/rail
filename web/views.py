from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from get_data.get_ticket import get_ticket
import json, random
from datetime import datetime
from web.models import *

def index(request):
    last = Station.objects.count()
    station = Station.objects.all()[random.randint(0, last)]
    if station.image_date and Timetable.objects.filter(station=station.cn):
        return render(request, 'index.html', {'cn': station.cn})
    else:
        return index(request)

def log(request):
    with open('get_data/data.log', 'r') as f:
        logs = f.read()
    logs = [log.split('-|-')[1:] for log in logs.split('||') if 'ERROR' in log and '-|-' in log][-100:][::-1]
    return render(request, 'monitor.html', {'logs': logs})


def station(request, cn):
    data = Station.objects.get(cn=cn)
    timetable = json.dumps(station_timetable(cn))
    return render(request, 'station.html',
                  {'station': cn, 'province': data.province, 'city': data.city, 'county': data.county,
                   'timetable': timetable})


def line(request, line):
    data = Line.objects.get(line=line)
    timetable = json.dumps(line_timetable(line))
    return render(request, 'line.html',
                  {'line': line, 'start': data.start, 'arrive': data.arrive, 'timetable': timetable})


def ticket(request, start, arrive, date):
    if len(date) < 3:
        year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        date = str(datetime(year, month + 1 if int(date) < day else month, int(date)).date())
    tickettable = json.dumps(get_ticket(start, arrive, date))
    return render(request, 'ticket.html', {'start': start, 'arrive': arrive, 'date': date, 'tickettable': tickettable})


def station_timetable(station):
    timetable = []
    for row in Timetable.objects.filter(station=station).order_by('leavetime'):
        line, arrivetime, leavetime, staytime = row.line, str(row.arrivetime), str(row.leavetime), row.staytime
        line_data = Line.objects.get(line=line)
        start = line_data.start
        arrive = line_data.arrive
        staytime = [staytime, '终', '始'][staytime if staytime in [-2, -1] else 0]
        if staytime == '始': arrivetime = '-' * 11
        if staytime == '终': leavetime = '-' * 11
        timetable.append([line, start, arrive, arrivetime, leavetime, staytime])
    return timetable


def line_timetable(line):
    timetable = []
    for row in Timetable.objects.filter(line=line.upper()).order_by('order'):
        order, station, arrivedate, arrivetime, leavedate, leavetime, staytime = row.order, row.station, row.arrivedate, str(
            row.arrivetime), row.leavedate, str(row.leavetime), row.staytime
        staytime = [staytime, '终', '始'][staytime if staytime in [-2, -1] else 0]
        if staytime == '始':
            arrivedate = '--'
            arrivetime = '-' * 11
        if staytime == '终':
            leavedate = '--'
            leavetime = '-' * 11
        timetable.append([order, station, arrivedate, arrivetime, leavedate, leavetime, staytime])
    return timetable
