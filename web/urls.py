from django.urls import path

from .views import *
from .wx import *

urlpatterns = [
    path('', index, name='index'),
    path('log', log, name='log'),
    path('station', station, {'station': 'index'}, name='station_index'),
    path('station/<station>', station, name='station'),
    path('line', line, {'line': 'index'}, name='line_index'),
    path('line/<line>', line, name='line'),
    path('city', city, {'city': 'index'}, name='city_index'),
    path('city/<city>', city, name='city'),
    path('data', data, name='data'),
    path('wx', wx),
]
