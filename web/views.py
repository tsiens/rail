from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import json


def index(request):
    return render(request, 'index.html')


def page(request, type, data):
    return render(request, 'page.html', {'type': type, 'data': data})


from data import *


def data(requests):
    type = requests.GET.get('type')
    if type == 'station':
        data = station(requests.GET.get('data'))
    elif type == 'line':
        data = line(requests.GET.get('data'))
    elif type == 'ticket':
        data = ticket(requests.GET.get('data'))
    else:
        data = []
    return HttpResponse(json.dumps(data), content_type='application/json')
