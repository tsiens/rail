from django.db.models import Q

from web.models import *


def search(key):
    key = key.upper()
    data = {'车站': [], '城市': [], '车次': []}
    for item in Station.objects.filter(Q(province__contains=key) | Q(city__contains=key) | Q(county__contains=key))[
                :10].values_list('province', 'city', 'county'):
        province, city, county = item
        if key in county:
            item_data = province + '-' + city + '-' + county
        elif key in city:
            item_data = province + '-' + city
        else:
            item_data = province
        if item_data not in data['城市']:
            data['城市'].append(item_data)
    line_stations = list(Timetable.objects.values_list('station', flat=True).distinct())
    data['车站'] = Station.objects.filter(Q(cn__contains=key), Q(cn__in=line_stations)).order_by('cn')[:10].values_list(
        'cn', flat=True)
    data['车次'] = list(Line.objects.filter(Q(line=key), ~Q(runtime=None)).values_list('line', flat=True)) + list(
        Line.objects.filter(Q(line__contains=key), ~Q(runtime=None)).order_by('line')[:10].values_list('line',
                                                                                                       flat=True))
    n = 0
    for k, v in data.items():
        n += len(v)
    return [n, data]


if __name__ == '__main__':
    print(search('杭州'))
