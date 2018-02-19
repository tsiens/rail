import random

from django.db.models import Q

from web.models import *


def luck():
    choice = random.randint(0, Timetable.objects.count() - 1)
    item = random.sample(['line', 'station', 'city'], 1)[0]
    if item == 'city':
        station = Timetable.objects.values_list('station', flat=True)[choice]
        keys = ['province', 'city', 'county']
        key = random.randint(1, len(keys))
        return [item, '-'.join(Station.objects.filter(cn=station).values_list(*keys[:key])[0])]
    else:
        return [item, Timetable.objects.values_list(item, flat=True)[choice]]

def search(key):
    key = key.upper()
    data = {'station': [], 'city': [], 'line': []}
    for item in Station.objects.filter(Q(province__contains=key) | Q(city__contains=key) | Q(county__contains=key))[
                :10].values_list('province', 'city', 'county'):
        province, city, county = item
        if key in county:
            item_data = province + '-' + city + '-' + county
        elif key in city:
            item_data = province + '-' + city
        else:
            item_data = province
        if item_data not in data['city']:
            data['city'].append(item_data)
    line_stations = list(Timetable.objects.values_list('station', flat=True).distinct())
    data['station'] = list(
        Station.objects.filter(Q(cn__contains=key), Q(cn__in=line_stations)).order_by('cn')[:10].values_list(
            'cn', flat=True))
    data['line'] = list(Line.objects.filter(Q(line=key), ~Q(runtime=None)).values_list('line', flat=True)) + list(
        Line.objects.filter(Q(line__contains=key), ~Q(runtime=None)).order_by('line')[:10].values_list('line',
                                                                                                       flat=True))
    n = 0
    for k, v in data.items():
        n += len(v)
    return [n, data]


if __name__ == '__main__':
    # print(search('杭州'))
    k, v = luck()
    if k in ['城市', '车站']:
        articles = [{
            'title': '推荐 %s' % v,
            'url': 'http://rail.qiangs.tech/%s/%s' % (k, v)
        }]
    else:
        start, arrive = Line.objects.filter(line=v).values_list('start', 'arrive')[0]
        articles = [{
            'title': '%s次 %s-%s' % (v, start, arrive),
            'image': qiniu_img_url % start,
            'url': 'http://rail.qiangs.tech/line/%s' % v
        }]
    if txt != '运气':
        articles.append({'title': '小的不才，无法识别 “%s”' % txt})
