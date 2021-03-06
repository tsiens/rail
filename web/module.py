import random

from django.db.models import Q

from web.models import *


def luck():
    choice = random.randint(0, Timetable.objects.count() - 1)
    item = random.sample(['line', 'station', 'city'], 1)[0]
    if item == 'city':
        station = Timetable.objects.values_list('station', flat=True)[choice]
        keys = ['province', 'city']
        key = random.randint(1, len(keys))
        return [item, '-'.join(Station.objects.filter(cn=station).values_list(*keys[:key])[0])]
    else:
        return [item, Timetable.objects.values_list(item, flat=True)[choice]]


def search(key):
    key = key.upper()
    data = {'station': [], 'city': [], 'line': []}
    for item in Station.objects.filter(Q(province__contains=key) | Q(city__contains=key))[:10].values_list('province',
                                                                                                           'city'):
        province, city = item
        if key in city:
            item_data = province + '-' + city
        else:
            item_data = province
        if item_data not in data['city']:
            data['city'].append(item_data)
    line_stations = list(Timetable.objects.values_list('station', flat=True).distinct())
    data['station'] = list(
        Station.objects.filter(Q(cn__contains=key), Q(cn__in=line_stations)).order_by('cn')[:10].values_list(
            'cn', flat=True))
    data['line'] = list(Line.objects.filter(
        Q(line=key) | Q(line__startswith=key + '/') | Q(line__endswith='/' + key) | Q(line__contains='/' + key + '/'),
        ~Q(runtime=None))[:1].values_list('line', flat=True))
    for line in list(Line.objects.filter(Q(line__contains=key), ~Q(runtime=None)).order_by(
            'line')[:10].values_list('line', flat=True)):
        if line not in data['line']:
            data['line'].append(line)
    return data


if __name__ == '__main__':
    print(search('杭州'))
