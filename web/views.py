from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from get_data.get_ticket import get_ticket
import json
from web.models import *

def index(request):
    return render(request, 'index.html')


def page(request, type, data):
    return render(request, 'page.html', {'type': type, 'data': data})


def data(requests):
    type = requests.GET.get('type')
    data = []
    if type == 'station':
        station = requests.GET.get('data')
        for row in Timetable.objects.filter(station=station).order_by('leavetime'):
            line, arrivetime, leavetime, staytime = row.line, str(row.arrivetime), str(row.leavetime), row.staytime
            staytime = [staytime, '终', '始'][staytime if staytime in [-2, -1] else 0]
            if staytime == '始': arrivetime = '-' * 11
            if staytime == '终': arrivetime = '-' * 11
            data.append([line, arrivetime, leavetime, staytime])
    elif type == 'line':
        line = requests.GET.get('data')
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
            data.append([order, station, arrivedate, arrivetime, leavedate, leavetime, staytime])
    elif type == 'ticket':
        start, arrive, date = requests.GET.get('data').split('|')
        data = get_ticket(start, arrive, date)
    else:
        data = []
    return HttpResponse(json.dumps(data), content_type='application/json')
