from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from web.models import *
import json


def station(request,cn):
    data=[]
    for row in Timetable.objects.filter(station=cn).order_by('leavetime'):
        if row.staytime==-1:
            staytime='始发'
        elif row.staytime==-2:
            staytime='终到'
        else:
            staytime = row.staytime
        data.append([row.line,str(row.arrivetime),str(row.leavetime),staytime])
    return HttpResponse(json.dumps(data),content_type='application/json')