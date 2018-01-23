from django.urls import path

from .views import *
from .wx import *

urlpatterns = [
    path('', index, name='index'),
    path('log', log, name='log'),
    path('station/<station>', station, name='station'),
    path('line/<line>', line, name='line'),
    path('city/<city>', city, name='city'),
    path('data', data, name='data'),
    path('wx', wx),
]
