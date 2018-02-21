import json
from datetime import *

from django.db.models import Count
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

import key
from web.module import *


def val(request):
    qiniu = 'http://qiniu.rail.qiangs.tech/station_img/'
    baidu_bak = key.baidu_bak
    amap_bak = key.amap_bak
    return locals()


def index(request):
    format = '.jpg?imageMogr2/auto-orient/thumbnail/x300/interlace/1/blur/1x0/quality/75|imageslim&time=%s' % str(
        datetime.now().date())
    line_stations = list(Timetable.objects.values_list('station', flat=True).distinct())
    image_stations = list(Station.objects.filter(Q(cn__in=line_stations), ~Q(image=None)).values_list('cn', flat=True))
    stations = random.sample(image_stations, 10)
    return render(request, 'index.html', locals())


def station(request, station):
    if station == 'index':
        format = '.jpg?imageMogr2/auto-orient/thumbnail/200x/interlace/1/blur/1x0/quality/75|imageslim&time=%s' % str(
            datetime.now().date())
        count = Timetable.objects.values('station').distinct().count()
        return render(request, 'station_index.html', locals())
    else:
        if Timetable.objects.filter(station=station):
            station, province, city, county = \
                Station.objects.filter(cn=station).values_list('cn', 'province', 'city', 'county')[0]
            return render(request, 'station.html', locals())
        else:
            err = '%s站不存在或暂未开通客运服务' % station
            return render(request, '404.html', locals())


def line(request, line):
    if line == 'index':
        line_codes = list(Line.objects.values_list('line', flat=True))
        line_codes = sorted(list(set([line[0] for line in line_codes])))
        return render(request, 'line_index.html', locals())
    else:
        line = line.upper()
        if Timetable.objects.filter(line__contains=line):
            lines = list(Line.objects.filter(
                Q(line=line) | Q(line__startswith=line + '/') | Q(line__endswith='/' + line) | Q(
                    line__contains='/' + line + '/'), ~Q(runtime=None))[:1].values_list('line', 'arrive',
                                                                                        'start')) + list(
                Line.objects.filter(Q(line__contains=line), ~Q(runtime=None)).order_by('line')[:1].values_list('line',
                                                                                                               'arrive',
                                                                                                               'start'))
            line, arrive, start = lines[0]
            return render(request, 'line.html', locals())
        else:
            err = '%s次不存在或无详细时刻信息' % line
            return render(request, '404.html', locals())


def city(request, city):
    return render(request, 'city.html', locals())


def data(request):
    type = request.POST.get('type')
    data = []
    if type == 'log':
        with open('get_data/data.log', 'r') as f:
            logs = f.read()
        data = [log.split('-|-')[1:] for log in logs.split('||') if 'ERROR' in log and '-|-' in log][-100:][::-1]
    elif type == 'station_index':
        start, end = int(request.POST.get('start')), int(request.POST.get('end'))
        image_stations = list(Station.objects.exclude(image=None).values_list('cn', flat=True))
        sort_stations = list(
            Timetable.objects.filter(station__in=image_stations).values('station').annotate(
                count=Count('line')).order_by('-count')[start:end].values_list('station', flat=True))
        stations = list(Station.objects.filter(cn__in=sort_stations).values_list('cn', 'province', 'city', 'county'))
        data = sorted(stations, key=lambda x: sort_stations.index(x[0]))
    elif type == 'line_index':
        data = []
        code = request.POST.get('code')
        for line in Line.objects.filter(Q(line__startswith=code), ~Q(runtime=None)).values_list('line', 'start',
                                                                                                'arrive'):
            data.append(line)
        data = sorted(data, key=lambda x: (x[0][0], int(x[0].split('/')[0][1:]) if len(x[0]) > 1 else 0))
    elif type == 'city':
        # data = {}
        # stations = list(Timetable.objects.values_list('station', flat=True).distinct())
        # for item in Station.objects.filter(cn__in=stations).values_list('cn', 'province', 'city', 'county'):
        #     cn, province, city, county = item
        #     if province not in data:
        #         data[province] = {}
        #     if city not in data[province]:
        #         data[province][city] = {}
        #     if county not in data[province][city]:
        #         data[province][city][county] = 1
        #     else:
        #         data[province][city][county]+=1
        data = {"\u5c71\u897f\u7701": {
            "\u8fd0\u57ce\u5e02": {"\u76d0\u6e56\u533a": 2, "\u6c38\u6d4e\u5e02": 2, "\u95fb\u559c\u53bf": 3,
                                   "\u82ae\u57ce\u53bf": 1, "\u6cb3\u6d25\u5e02": 1, "\u7a37\u5c71\u53bf": 1,
                                   "\u65b0\u7edb\u53bf": 1},
            "\u5927\u540c\u5e02": {"\u7075\u4e18\u53bf": 5, "\u57ce\u533a": 1, "\u77ff\u533a": 1,
                                   "\u5929\u9547\u53bf": 1, "\u9633\u9ad8\u53bf": 1, "\u65b0\u8363\u533a": 1,
                                   "\u5357\u90ca\u533a": 1},
            "\u9633\u6cc9\u5e02": {"\u5e73\u5b9a\u53bf": 2, "\u57ce\u533a": 1, "\u76c2\u53bf": 1},
            "\u5ffb\u5dde\u5e02": {"\u5ca2\u5c9a\u53bf": 3, "\u7e41\u5cd9\u53bf": 5, "\u4ee3\u53bf": 4,
                                   "\u5ffb\u5e9c\u533a": 3, "\u5b9a\u8944\u53bf": 2, "\u5b81\u6b66\u53bf": 1,
                                   "\u795e\u6c60\u53bf": 1, "\u4e94\u5be8\u53bf": 1, "\u539f\u5e73\u5e02": 2},
            "\u5415\u6881\u5e02": {"\u5b5d\u4e49\u5e02": 5, "\u6c7e\u9633\u5e02": 1, "\u4ea4\u57ce\u53bf": 1,
                                   "\u79bb\u77f3\u533a": 1, "\u67f3\u6797\u53bf": 1, "\u6587\u6c34\u53bf": 1},
            "\u957f\u6cbb\u5e02": {"\u90ca\u533a": 3, "\u8944\u57a3\u53bf": 1, "\u6c81\u53bf": 1,
                                   "\u9ece\u57ce\u53bf": 1, "\u6f5e\u57ce\u5e02": 1, "\u6b66\u4e61\u53bf": 1,
                                   "\u957f\u6cbb\u53bf": 1, "\u957f\u5b50\u53bf": 2},
            "\u592a\u539f\u5e02": {"\u5c16\u8349\u576a\u533a": 1, "\u9633\u66f2\u53bf": 2, "\u53e4\u4ea4\u5e02": 3,
                                   "\u6e05\u5f90\u53bf": 1, "\u674f\u82b1\u5cad\u533a": 1, "\u5c0f\u5e97\u533a": 1,
                                   "\u8fce\u6cfd\u533a": 1},
            "\u664b\u57ce\u5e02": {"\u9ad8\u5e73\u5e02": 4, "\u57ce\u533a": 2, "\u6cfd\u5dde\u53bf": 4},
            "\u4e34\u6c7e\u5e02": {"\u6d2a\u6d1e\u53bf": 3, "\u4faf\u9a6c\u5e02": 2, "\u970d\u5dde\u5e02": 2,
                                   "\u5c27\u90fd\u533a": 2, "\u8944\u6c7e\u53bf": 2},
            "\u6714\u5dde\u5e02": {"\u6000\u4ec1\u53bf": 2, "\u5c71\u9634\u53bf": 2, "\u6714\u57ce\u533a": 2,
                                   "\u5e94\u53bf": 1},
            "\u664b\u4e2d\u5e02": {"\u4ecb\u4f11\u5e02": 3, "\u6986\u6b21\u533a": 2, "\u7075\u77f3\u53bf": 2,
                                   "\u5e73\u9065\u53bf": 2, "\u7941\u53bf": 2, "\u5bff\u9633\u53bf": 2,
                                   "\u592a\u8c37\u53bf": 2, "\u6986\u793e\u53bf": 1}}, "\u9ed1\u9f99\u6c5f\u7701": {
            "\u54c8\u5c14\u6ee8\u5e02": {"\u963f\u57ce\u533a": 5, "\u4e94\u5e38\u5e02": 6, "\u547c\u5170\u533a": 5,
                                         "\u9999\u574a\u533a": 4, "\u677e\u5317\u533a": 4, "\u5357\u5c97\u533a": 2,
                                         "\u53cc\u57ce\u533a": 4, "\u5c1a\u5fd7\u5e02": 6, "\u5e73\u623f\u533a": 1,
                                         "\u9053\u5916\u533a": 1, "\u5df4\u5f66\u53bf": 2, "\u9053\u91cc\u533a": 1},
            "\u7ee5\u5316\u5e02": {"\u5b89\u8fbe\u5e02": 2, "\u6d77\u4f26\u5e02": 4, "\u8087\u4e1c\u5e02": 5,
                                   "\u5e86\u5b89\u53bf": 1, "\u5317\u6797\u533a": 4, "\u7ee5\u68f1\u53bf": 1},
            "\u9ed1\u6cb3\u5e02": {"\u5317\u5b89\u5e02": 4, "\u7231\u8f89\u533a": 2,
                                   "\u4e94\u5927\u8fde\u6c60\u5e02": 2, "\u5ae9\u6c5f\u53bf": 7,
                                   "\u5b59\u5434\u53bf": 1},
            "\u4e03\u53f0\u6cb3\u5e02": {"\u52c3\u5229\u53bf": 7, "\u65b0\u5174\u533a": 1},
            "\u7261\u4e39\u6c5f\u5e02": {"\u7a46\u68f1\u5e02": 4, "\u6797\u53e3\u53bf": 12, "\u6d77\u6797\u5e02": 8,
                                         "\u5b81\u5b89\u5e02": 7, "\u9633\u660e\u533a": 1, "\u4e1c\u5b89\u533a": 1,
                                         "\u7ee5\u82ac\u6cb3\u5e02": 1, "\u4e1c\u5b81\u5e02": 1,
                                         "\u897f\u5b89\u533a": 1},
            "\u9e64\u5c97\u5e02": {"\u841d\u5317\u53bf": 2, "\u5411\u9633\u533a": 1, "\u4e1c\u5c71\u533a": 2},
            "\u53cc\u9e2d\u5c71\u5e02": {"\u96c6\u8d24\u53bf": 5, "\u5b9d\u6e05\u53bf": 2, "\u53cb\u8c0a\u53bf": 3,
                                         "\u5c16\u5c71\u533a": 1},
            "\u4f0a\u6625\u5e02": {"\u5357\u5c94\u533a": 5, "\u5e26\u5cad\u533a": 2, "\u91d1\u5c71\u5c6f\u533a": 1,
                                   "\u94c1\u529b\u5e02": 7, "\u7f8e\u6eaa\u533a": 1, "\u6c64\u65fa\u6cb3\u533a": 1,
                                   "\u4e0a\u7518\u5cad\u533a": 1, "\u7ea2\u661f\u533a": 1,
                                   "\u4e4c\u4f0a\u5cad\u533a": 1, "\u4e94\u8425\u533a": 1, "\u65b0\u9752\u533a": 1,
                                   "\u897f\u6797\u533a": 2, "\u4f0a\u6625\u533a": 1, "\u53cb\u597d\u533a": 2},
            "\u9e21\u897f\u5e02": {"\u6ef4\u9053\u533a": 2, "\u864e\u6797\u5e02": 6, "\u9e21\u4e1c\u53bf": 3,
                                   "\u5bc6\u5c71\u5e02": 6, "\u9e21\u51a0\u533a": 1, "\u68a8\u6811\u533a": 2,
                                   "\u9ebb\u5c71\u533a": 3, "\u6052\u5c71\u533a": 1},
            "\u4f73\u6728\u65af\u5e02": {"\u629a\u8fdc\u5e02": 4, "\u5bcc\u9526\u5e02": 5, "\u6866\u5357\u53bf": 3,
                                         "\u6c64\u539f\u53bf": 4, "\u540c\u6c5f\u5e02": 3, "\u524d\u8fdb\u533a": 1,
                                         "\u90ca\u533a": 4, "\u6866\u5ddd\u53bf": 3},
            "\u9f50\u9f50\u54c8\u5c14\u5e02": {"\u6cf0\u6765\u53bf": 5, "\u5bcc\u88d5\u53bf": 7,
                                               "\u5bcc\u62c9\u5c14\u57fa\u533a": 2, "\u514b\u4e1c\u53bf": 1,
                                               "\u514b\u5c71\u53bf": 2, "\u8bb7\u6cb3\u5e02": 8,
                                               "\u9f99\u6c5f\u53bf": 1, "\u78be\u5b50\u5c71\u533a": 2,
                                               "\u94c1\u950b\u533a": 1, "\u9f99\u6c99\u533a": 1,
                                               "\u6602\u6602\u6eaa\u533a": 6, "\u4f9d\u5b89\u53bf": 1,
                                               "\u5efa\u534e\u533a": 1},
            "\u5927\u5e86\u5e02": {"\u8428\u5c14\u56fe\u533a": 1, "\u9f99\u51e4\u533a": 2,
                                   "\u8ba9\u80e1\u8def\u533a": 2, "\u5927\u540c\u533a": 4,
                                   "\u675c\u5c14\u4f2f\u7279\u8499\u53e4\u65cf\u81ea\u6cbb\u53bf": 2,
                                   "\u8087\u6e90\u53bf": 1, "\u7ea2\u5c97\u533a": 1},
            "\u5927\u5174\u5b89\u5cad\u5730\u533a": {"\u6f20\u6cb3\u53bf": 4, "\u52a0\u683c\u8fbe\u5947\u533a": 4,
                                                     "\u547c\u739b\u53bf": 8, "\u5854\u6cb3\u53bf": 5}},
                "\u6c5f\u897f\u7701": {
                    "\u4e5d\u6c5f\u5e02": {"\u6c38\u4fee\u53bf": 1, "\u5fb7\u5b89\u53bf": 1, "\u90fd\u660c\u53bf": 1,
                                           "\u5171\u9752\u57ce\u5e02": 1, "\u6e56\u53e3\u53bf": 1,
                                           "\u6fc2\u6eaa\u533a": 1, "\u4e5d\u6c5f\u53bf": 1, "\u5f6d\u6cfd\u53bf": 1,
                                           "\u745e\u660c\u5e02": 2},
                    "\u4e0a\u9976\u5e02": {"\u5fb7\u5174\u5e02": 2, "\u6a2a\u5cf0\u53bf": 1, "\u9131\u9633\u53bf": 1,
                                           "\u4fe1\u5dde\u533a": 1, "\u4e0a\u9976\u53bf": 1, "\u4e07\u5e74\u53bf": 1,
                                           "\u5a7a\u6e90\u53bf": 1, "\u7389\u5c71\u53bf": 2, "\u5f0b\u9633\u53bf": 1},
                    "\u8d63\u5dde\u5e02": {"\u5b9a\u5357\u53bf": 1, "\u5927\u4f59\u53bf": 1, "\u4fe1\u4e30\u53bf": 1,
                                           "\u5174\u56fd\u53bf": 1, "\u7ae0\u8d21\u533a": 1, "\u745e\u91d1\u5e02": 1,
                                           "\u9f99\u5357\u53bf": 1, "\u4f1a\u660c\u53bf": 1, "\u4e8e\u90fd\u53bf": 1},
                    "\u629a\u5dde\u5e02": {"\u4e1c\u4e61\u533a": 2, "\u4e34\u5ddd\u533a": 1, "\u5357\u57ce\u53bf": 1,
                                           "\u5357\u4e30\u53bf": 1, "\u8d44\u6eaa\u53bf": 1},
                    "\u5409\u5b89\u5e02": {"\u65b0\u5e72\u53bf": 1, "\u5ce1\u6c5f\u53bf": 1,
                                           "\u4e95\u5188\u5c71\u5e02": 2, "\u6cf0\u548c\u53bf": 1,
                                           "\u9752\u539f\u533a": 1},
                    "\u5b9c\u6625\u5e02": {"\u4e30\u57ce\u5e02": 1, "\u9ad8\u5b89\u5e02": 1, "\u8881\u5dde\u533a": 1,
                                           "\u6a1f\u6811\u5e02": 2},
                    "\u65b0\u4f59\u5e02": {"\u5206\u5b9c\u53bf": 1, "\u6e1d\u6c34\u533a": 2},
                    "\u9e70\u6f6d\u5e02": {"\u8d35\u6eaa\u5e02": 2, "\u6708\u6e56\u533a": 1},
                    "\u666f\u5fb7\u9547\u5e02": {"\u73e0\u5c71\u533a": 2, "\u4e50\u5e73\u5e02": 1},
                    "\u5357\u660c\u5e02": {"\u8fdb\u8d24\u53bf": 2, "\u9752\u5c71\u6e56\u533a": 1,
                                           "\u65b0\u5efa\u533a": 1, "\u5357\u660c\u53bf": 1},
                    "\u840d\u4e61\u5e02": {"\u4e0a\u6817\u53bf": 1, "\u5b89\u6e90\u533a": 2}}, "\u6d77\u5357\u7701": {
                "\u76f4\u5c5e": {"\u6f84\u8fc8\u53bf": 2, "\u743c\u6d77\u5e02": 2, "\u4e34\u9ad8\u53bf": 1,
                                 "\u4e50\u4e1c\u9ece\u65cf\u81ea\u6cbb\u53bf": 3,
                                 "\u9675\u6c34\u9ece\u65cf\u81ea\u6cbb\u53bf": 1, "\u4e1c\u65b9\u5e02": 2,
                                 "\u660c\u6c5f\u9ece\u65cf\u81ea\u6cbb\u53bf": 1, "\u4e07\u5b81\u5e02": 2,
                                 "\u6587\u660c\u5e02": 1}, "\u510b\u5dde\u5e02": {"\u76f4\u5c5e": 2},
                "\u4e09\u4e9a\u5e02": {"\u5929\u6daf\u533a": 1, "\u5409\u9633\u533a": 3, "\u5d16\u5dde\u533a": 1},
                "\u6d77\u53e3\u5e02": {"\u9f99\u534e\u533a": 2, "\u7f8e\u5170\u533a": 1, "\u79c0\u82f1\u533a": 1}},
                "\u6cb3\u5357\u7701": {
                    "\u5b89\u9633\u5e02": {"\u5b89\u9633\u53bf": 1, "\u5317\u5173\u533a": 1, "\u6c64\u9634\u53bf": 1},
                    "\u5e73\u9876\u5c71\u5e02": {"\u5b9d\u4e30\u53bf": 1, "\u9c81\u5c71\u53bf": 1,
                                                 "\u6e5b\u6cb3\u533a": 1, "\u6c5d\u5dde\u5e02": 1},
                    "\u8bb8\u660c\u5e02": {"\u957f\u845b\u5e02": 1, "\u5efa\u5b89\u533a": 2, "\u9b4f\u90fd\u533a": 1},
                    "\u65b0\u4e61\u5e02": {"\u957f\u57a3\u53bf": 1, "\u7ea2\u65d7\u533a": 1, "\u83b7\u5609\u53bf": 1,
                                           "\u536b\u8f89\u5e02": 1, "\u536b\u6ee8\u533a": 1},
                    "\u5357\u9633\u5e02": {"\u9093\u5dde\u5e02": 1, "\u5357\u53ec\u53bf": 1, "\u5367\u9f99\u533a": 1,
                                           "\u5185\u4e61\u53bf": 1, "\u6850\u67cf\u53bf": 1, "\u5510\u6cb3\u53bf": 1,
                                           "\u897f\u5ce1\u53bf": 1, "\u9547\u5e73\u53bf": 1},
                    "\u5546\u4e18\u5e02": {"\u590f\u9091\u53bf": 1, "\u865e\u57ce\u53bf": 1, "\u6c11\u6743\u53bf": 2,
                                           "\u5b81\u9675\u53bf": 1, "\u6c38\u57ce\u5e02": 1, "\u6881\u56ed\u533a": 2},
                    "\u4fe1\u9633\u5e02": {"\u606f\u53bf": 1, "\u5149\u5c71\u53bf": 1, "\u56fa\u59cb\u53bf": 1,
                                           "\u6dee\u6ee8\u53bf": 1, "\u6f62\u5ddd\u53bf": 1, "\u7f57\u5c71\u53bf": 1,
                                           "\u5e73\u6865\u533a": 3, "\u5546\u57ce\u53bf": 1, "\u65b0\u53bf": 1},
                    "\u5468\u53e3\u5e02": {"\u9879\u57ce\u5e02": 1, "\u6c88\u4e18\u53bf": 1, "\u5ddd\u6c47\u533a": 1},
                    "\u7126\u4f5c\u5e02": {"\u4fee\u6b66\u53bf": 1, "\u89e3\u653e\u533a": 1, "\u6b66\u965f\u53bf": 1,
                                           "\u535a\u7231\u53bf": 2},
                    "\u90d1\u5dde\u5e02": {"\u65b0\u90d1\u5e02": 1, "\u5de9\u4e49\u5e02": 2, "\u60e0\u6d4e\u533a": 2,
                                           "\u4e2d\u725f\u53bf": 1, "\u8365\u9633\u5e02": 1, "\u91d1\u6c34\u533a": 1,
                                           "\u4e8c\u4e03\u533a": 1},
                    "\u6d1b\u9633\u5e02": {"\u6d1b\u9f99\u533a": 2, "\u700d\u6cb3\u56de\u65cf\u533a": 1,
                                           "\u897f\u5de5\u533a": 1, "\u65b0\u5b89\u53bf": 1, "\u5043\u5e08\u5e02": 1},
                    "\u9e64\u58c1\u5e02": {"\u6dc7\u6ee8\u533a": 2}, "\u76f4\u5c5e": {"\u6d4e\u6e90\u5e02": 1},
                    "\u5f00\u5c01\u5e02": {"\u9f99\u4ead\u533a": 2, "\u79b9\u738b\u53f0\u533a": 1,
                                           "\u5170\u8003\u53bf": 2},
                    "\u4e09\u95e8\u5ce1\u5e02": {"\u7075\u5b9d\u5e02": 2, "\u6e11\u6c60\u53bf": 2,
                                                 "\u9655\u5dde\u533a": 2, "\u6e56\u6ee8\u533a": 1,
                                                 "\u4e49\u9a6c\u5e02": 1},
                    "\u6f2f\u6cb3\u5e02": {"\u6e90\u6c47\u533a": 1, "\u4e34\u988d\u53bf": 1, "\u53ec\u9675\u533a": 1},
                    "\u6fee\u9633\u5e02": {"\u534e\u9f99\u533a": 1, "\u53f0\u524d\u53bf": 1},
                    "\u9a7b\u9a6c\u5e97\u5e02": {"\u786e\u5c71\u53bf": 1, "\u9042\u5e73\u53bf": 1,
                                                 "\u897f\u5e73\u53bf": 1, "\u9a7f\u57ce\u533a": 2}},
                "\u4e91\u5357\u7701": {
                    "\u66f2\u9756\u5e02": {"\u7f57\u5e73\u53bf": 5, "\u6cbe\u76ca\u533a": 4, "\u5e08\u5b97\u53bf": 5,
                                           "\u5bcc\u6e90\u53bf": 5, "\u9646\u826f\u53bf": 1, "\u9a6c\u9f99\u53bf": 3,
                                           "\u9e92\u9e9f\u533a": 1, "\u5ba3\u5a01\u5e02": 1},
                    "\u662d\u901a\u5e02": {"\u76d0\u6d25\u53bf": 1, "\u6c34\u5bcc\u53bf": 1, "\u662d\u9633\u533a": 2},
                    "\u7389\u6eaa\u5e02": {"\u7ea2\u5854\u533a": 1, "\u901a\u6d77\u53bf": 1},
                    "\u695a\u96c4\u5f5d\u65cf\u81ea\u6cbb\u5dde": {"\u7984\u4e30\u53bf": 6, "\u695a\u96c4\u5e02": 1,
                                                                   "\u5143\u8c0b\u53bf": 6, "\u59da\u5b89\u53bf": 2,
                                                                   "\u725f\u5b9a\u53bf": 3, "\u6c38\u4ec1\u53bf": 1,
                                                                   "\u5357\u534e\u53bf": 1},
                    "\u6606\u660e\u5e02": {"\u5b9c\u826f\u53bf": 6, "\u77f3\u6797\u5f5d\u65cf\u81ea\u6cbb\u53bf": 6,
                                           "\u5448\u8d21\u533a": 3, "\u664b\u5b81\u533a": 1, "\u5b98\u6e21\u533a": 2,
                                           "\u5d69\u660e\u53bf": 3},
                    "\u5927\u7406\u767d\u65cf\u81ea\u6cbb\u5dde": {"\u7965\u4e91\u53bf": 3, "\u5927\u7406\u5e02": 1,
                                                                   "\u9e64\u5e86\u53bf": 1, "\u5f25\u6e21\u53bf": 1},
                    "\u6587\u5c71\u58ee\u65cf\u82d7\u65cf\u81ea\u6cbb\u5dde": {"\u5bcc\u5b81\u53bf": 1,
                                                                               "\u5e7f\u5357\u53bf": 1,
                                                                               "\u4e18\u5317\u53bf": 1},
                    "\u7ea2\u6cb3\u54c8\u5c3c\u65cf\u5f5d\u65cf\u81ea\u6cbb\u5dde": {
                        "\u6cb3\u53e3\u7476\u65cf\u81ea\u6cbb\u53bf": 1, "\u5efa\u6c34\u53bf": 2,
                        "\u8499\u81ea\u5e02": 2, "\u5f25\u52d2\u5e02": 1,
                        "\u5c4f\u8fb9\u82d7\u65cf\u81ea\u6cbb\u53bf": 1},
                    "\u4e3d\u6c5f\u5e02": {"\u7389\u9f99\u7eb3\u897f\u65cf\u81ea\u6cbb\u53bf": 1}},
                "\u6e56\u5357\u7701": {"\u76ca\u9633\u5e02": {"\u8d6b\u5c71\u533a": 1, "\u5b89\u5316\u53bf": 1},
                                       "\u6c38\u5dde\u5e02": {"\u51b7\u6c34\u6ee9\u533a": 1, "\u4e1c\u5b89\u53bf": 1,
                                                              "\u9053\u53bf": 1,
                                                              "\u6c5f\u534e\u7476\u65cf\u81ea\u6cbb\u53bf": 1,
                                                              "\u6c5f\u6c38\u53bf": 1, "\u7941\u9633\u53bf": 1,
                                                              "\u53cc\u724c\u53bf": 1, "\u96f6\u9675\u533a": 1},
                                       "\u90f4\u5dde\u5e02": {"\u5b89\u4ec1\u53bf": 1, "\u82cf\u4ed9\u533a": 1,
                                                              "\u5317\u6e56\u533a": 1},
                                       "\u957f\u6c99\u5e02": {"\u671b\u57ce\u533a": 2, "\u8299\u84c9\u533a": 1,
                                                              "\u96e8\u82b1\u533a": 5, "\u5cb3\u9e93\u533a": 4,
                                                              "\u5f00\u798f\u533a": 1, "\u5929\u5fc3\u533a": 3},
                                       "\u682a\u6d32\u5e02": {"\u8336\u9675\u53bf": 1, "\u77f3\u5cf0\u533a": 2,
                                                              "\u8377\u5858\u533a": 2, "\u82a6\u6dde\u533a": 1,
                                                              "\u91b4\u9675\u5e02": 2, "\u708e\u9675\u53bf": 1,
                                                              "\u6538\u53bf": 1, "\u5929\u5143\u533a": 1},
                                       "\u5f20\u5bb6\u754c\u5e02": {"\u6148\u5229\u53bf": 1, "\u6c38\u5b9a\u533a": 1},
                                       "\u6000\u5316\u5e02": {"\u8fb0\u6eaa\u53bf": 1, "\u6e86\u6d66\u53bf": 2,
                                                              "\u65b0\u6643\u4f97\u65cf\u81ea\u6cbb\u53bf": 1,
                                                              "\u9e64\u57ce\u533a": 2,
                                                              "\u9756\u5dde\u82d7\u65cf\u4f97\u65cf\u81ea\u6cbb\u53bf": 1,
                                                              "\u901a\u9053\u4f97\u65cf\u81ea\u6cbb\u53bf": 2,
                                                              "\u4f1a\u540c\u53bf": 1,
                                                              "\u82b7\u6c5f\u4f97\u65cf\u81ea\u6cbb\u53bf": 1},
                                       "\u6e58\u6f6d\u5e02": {"\u6e58\u6f6d\u53bf": 1, "\u97f6\u5c71\u5e02": 1,
                                                              "\u5cb3\u5858\u533a": 3, "\u96e8\u6e56\u533a": 1,
                                                              "\u6e58\u4e61\u5e02": 1},
                                       "\u5a04\u5e95\u5e02": {"\u65b0\u5316\u53bf": 2, "\u6d9f\u6e90\u5e02": 1,
                                                              "\u5a04\u661f\u533a": 2, "\u53cc\u5cf0\u53bf": 1,
                                                              "\u51b7\u6c34\u6c5f\u5e02": 1},
                                       "\u90b5\u9633\u5e02": {"\u90b5\u4e1c\u53bf": 1, "\u65b0\u90b5\u53bf": 1,
                                                              "\u5927\u7965\u533a": 1},
                                       "\u8861\u9633\u5e02": {"\u8861\u5c71\u53bf": 1, "\u8861\u5357\u53bf": 1,
                                                              "\u73e0\u6656\u533a": 1, "\u8012\u9633\u5e02": 2,
                                                              "\u7941\u4e1c\u53bf": 1},
                                       "\u6e58\u897f\u571f\u5bb6\u65cf\u82d7\u65cf\u81ea\u6cbb\u5dde": {
                                           "\u5409\u9996\u5e02": 1, "\u53e4\u4e08\u53bf": 1},
                                       "\u5e38\u5fb7\u5e02": {"\u6fa7\u53bf": 1, "\u77f3\u95e8\u53bf": 1,
                                                              "\u6b66\u9675\u533a": 1},
                                       "\u5cb3\u9633\u5e02": {"\u6c68\u7f57\u5e02": 1, "\u5cb3\u9633\u697c\u533a": 2}},
                "\u6c5f\u82cf\u7701": {
                    "\u76d0\u57ce\u5e02": {"\u4ead\u6e56\u533a": 1, "\u961c\u5b81\u53bf": 1, "\u4e1c\u53f0\u5e02": 1},
                    "\u82cf\u5dde\u5e02": {"\u6606\u5c71\u5e02": 4, "\u864e\u4e18\u533a": 1, "\u5434\u4e2d\u533a": 1,
                                           "\u76f8\u57ce\u533a": 1, "\u59d1\u82cf\u533a": 1},
                    "\u6dee\u5b89\u5e02": {"\u6dee\u9634\u533a": 1},
                    "\u9547\u6c5f\u5e02": {"\u53e5\u5bb9\u5e02": 2, "\u4e39\u9633\u5e02": 2, "\u4e39\u5f92\u533a": 2,
                                           "\u6da6\u5dde\u533a": 1},
                    "\u5e38\u5dde\u5e02": {"\u5929\u5b81\u533a": 1, "\u65b0\u5317\u533a": 1, "\u6ea7\u9633\u5e02": 2,
                                           "\u6b66\u8fdb\u533a": 1},
                    "\u8fde\u4e91\u6e2f\u5e02": {"\u4e1c\u6d77\u53bf": 1, "\u8fde\u4e91\u533a": 1},
                    "\u5bbf\u8fc1\u5e02": {"\u6cad\u9633\u53bf": 1, "\u5bbf\u57ce\u533a": 1, "\u6cd7\u9633\u53bf": 1},
                    "\u5357\u901a\u5e02": {"\u5982\u4e1c\u53bf": 2, "\u6d77\u5b89\u53bf": 1, "\u6e2f\u95f8\u533a": 1,
                                           "\u5982\u768b\u5e02": 1},
                    "\u65e0\u9521\u5e02": {"\u65b0\u5434\u533a": 1, "\u60e0\u5c71\u533a": 1, "\u9521\u5c71\u533a": 1,
                                           "\u6881\u6eaa\u533a": 1, "\u5b9c\u5174\u5e02": 1},
                    "\u5357\u4eac\u5e02": {"\u6c5f\u5b81\u533a": 3, "\u6ea7\u6c34\u533a": 1, "\u7384\u6b66\u533a": 1,
                                           "\u6816\u971e\u533a": 1},
                    "\u5f90\u5dde\u5e02": {"\u90b3\u5dde\u5e02": 1, "\u8d3e\u6c6a\u533a": 1, "\u65b0\u6c82\u5e02": 1,
                                           "\u4e91\u9f99\u533a": 1},
                    "\u626c\u5dde\u5e02": {"\u6c5f\u90fd\u533a": 1, "\u9097\u6c5f\u533a": 1},
                    "\u6cf0\u5dde\u5e02": {"\u59dc\u5830\u533a": 1, "\u6d77\u9675\u533a": 1}}, "\u5317\u4eac\u5e02": {
                "\u76f4\u5c5e": {"\u623f\u5c71\u533a": 9, "\u4e1c\u57ce\u533a": 1, "\u671d\u9633\u533a": 1,
                                 "\u6000\u67d4\u533a": 4, "\u4e30\u53f0\u533a": 3, "\u987a\u4e49\u533a": 3,
                                 "\u660c\u5e73\u533a": 4, "\u5927\u5174\u533a": 1, "\u5ef6\u5e86\u533a": 1,
                                 "\u5bc6\u4e91\u533a": 2, "\u77f3\u666f\u5c71\u533a": 1, "\u901a\u5dde\u533a": 2}},
                "\u91cd\u5e86\u5e02": {
                    "\u76f4\u5c5e": {"\u9149\u9633\u571f\u5bb6\u65cf\u82d7\u65cf\u81ea\u6cbb\u53bf": 1,
                                     "\u5317\u789a\u533a": 1, "\u957f\u5bff\u533a": 2, "\u6e1d\u4e2d\u533a": 1,
                                     "\u6e1d\u5317\u533a": 1, "\u57ab\u6c5f\u53bf": 1,
                                     "\u79c0\u5c71\u571f\u5bb6\u65cf\u82d7\u65cf\u81ea\u6cbb\u53bf": 1,
                                     "\u6c5f\u5317\u533a": 1, "\u6daa\u9675\u533a": 2, "\u5927\u8db3\u533a": 1,
                                     "\u4e30\u90fd\u53bf": 1, "\u74a7\u5c71\u533a": 1, "\u6881\u5e73\u533a": 2,
                                     "\u77f3\u67f1\u571f\u5bb6\u65cf\u81ea\u6cbb\u53bf": 1,
                                     "\u5f6d\u6c34\u82d7\u65cf\u571f\u5bb6\u65cf\u81ea\u6cbb\u53bf": 1,
                                     "\u9ed4\u6c5f\u533a": 1, "\u8363\u660c\u533a": 1, "\u6f7c\u5357\u533a": 1,
                                     "\u5408\u5ddd\u533a": 1, "\u6b66\u9686\u533a": 1, "\u6c38\u5ddd\u533a": 1,
                                     "\u4e07\u5dde\u533a": 2, "\u6c99\u576a\u575d\u533a": 2, "\u7da6\u6c5f\u533a": 2,
                                     "\u6c5f\u6d25\u533a": 1}}, "\u5409\u6797\u7701": {
                "\u767d\u57ce\u5e02": {"\u5927\u5b89\u5e02": 4, "\u6d2e\u5317\u533a": 4, "\u6d2e\u5357\u5e02": 2,
                                       "\u901a\u6986\u53bf": 1, "\u9547\u8d49\u53bf": 1},
                "\u5ef6\u8fb9\u671d\u9c9c\u65cf\u81ea\u6cbb\u5dde": {"\u5b89\u56fe\u53bf": 7, "\u6c6a\u6e05\u53bf": 5,
                                                                     "\u9f99\u4e95\u5e02": 3, "\u6566\u5316\u5e02": 4,
                                                                     "\u548c\u9f99\u5e02": 3, "\u73f2\u6625\u5e02": 1,
                                                                     "\u56fe\u4eec\u5e02": 2, "\u5ef6\u5409\u5e02": 1},
                "\u5409\u6797\u5e02": {"\u86df\u6cb3\u5e02": 7, "\u660c\u9091\u533a": 4, "\u8212\u5170\u5e02": 4,
                                       "\u6c38\u5409\u53bf": 2, "\u78d0\u77f3\u5e02": 3, "\u9f99\u6f6d\u533a": 6},
                "\u8fbd\u6e90\u5e02": {"\u4e1c\u8fbd\u53bf": 2, "\u4e1c\u4e30\u53bf": 1, "\u9f99\u5c71\u533a": 1},
                "\u957f\u6625\u5e02": {"\u5fb7\u60e0\u5e02": 4, "\u5bbd\u57ce\u533a": 4, "\u7eff\u56ed\u533a": 1,
                                       "\u671d\u9633\u533a": 1, "\u519c\u5b89\u53bf": 4, "\u4e5d\u53f0\u533a": 4,
                                       "\u53cc\u9633\u533a": 1, "\u6986\u6811\u5e02": 5, "\u4e8c\u9053\u533a": 2},
                "\u677e\u539f\u5e02": {"\u6276\u4f59\u5e02": 4,
                                       "\u524d\u90ed\u5c14\u7f57\u65af\u8499\u53e4\u65cf\u81ea\u6cbb\u53bf": 3,
                                       "\u4e7e\u5b89\u53bf": 1, "\u957f\u5cad\u53bf": 1, "\u5b81\u6c5f\u533a": 1},
                "\u901a\u5316\u5e02": {"\u8f89\u5357\u53bf": 1, "\u4e8c\u9053\u6c5f\u533a": 5, "\u901a\u5316\u53bf": 4,
                                       "\u96c6\u5b89\u5e02": 4, "\u67f3\u6cb3\u53bf": 3, "\u6885\u6cb3\u53e3\u5e02": 2,
                                       "\u4e1c\u660c\u533a": 1},
                "\u767d\u5c71\u5e02": {"\u6d51\u6c5f\u533a": 3, "\u4e34\u6c5f\u5e02": 3, "\u629a\u677e\u53bf": 13,
                                       "\u6c5f\u6e90\u533a": 9},
                "\u56db\u5e73\u5e02": {"\u516c\u4e3b\u5cad\u5e02": 4, "\u68a8\u6811\u53bf": 1, "\u53cc\u8fbd\u5e02": 2,
                                       "\u94c1\u4e1c\u533a": 2, "\u94c1\u897f\u533a": 1,
                                       "\u4f0a\u901a\u6ee1\u65cf\u81ea\u6cbb\u53bf": 1}}, "\u6cb3\u5317\u7701": {
                "\u4fdd\u5b9a\u5e02": {"\u6d9e\u6e90\u53bf": 6, "\u6d9e\u6c34\u53bf": 4, "\u83b2\u6c60\u533a": 2,
                                       "\u5b9a\u5dde\u5e02": 2, "\u96c4\u53bf": 1, "\u5bb9\u57ce\u53bf": 1,
                                       "\u9ad8\u7891\u5e97\u5e02": 2, "\u6613\u53bf": 4, "\u5f90\u6c34\u533a": 1,
                                       "\u6dbf\u5dde\u5e02": 2},
                "\u5eca\u574a\u5e02": {"\u4e09\u6cb3\u5e02": 2, "\u9738\u5dde\u5e02": 3, "\u5e7f\u9633\u533a": 1,
                                       "\u5b89\u6b21\u533a": 1},
                "\u90af\u90f8\u5e02": {"\u6b66\u5b89\u5e02": 7, "\u78c1\u53bf": 1, "\u90af\u5c71\u533a": 1,
                                       "\u4e1b\u53f0\u533a": 1, "\u6d89\u53bf": 4},
                "\u627f\u5fb7\u5e02": {"\u6ee6\u5e73\u53bf": 11, "\u9e70\u624b\u8425\u5b50\u77ff\u533a": 2,
                                       "\u627f\u5fb7\u53bf": 11, "\u53cc\u6865\u533a": 3,
                                       "\u56f4\u573a\u6ee1\u65cf\u8499\u53e4\u65cf\u81ea\u6cbb\u53bf": 9,
                                       "\u9686\u5316\u53bf": 9, "\u5174\u9686\u53bf": 7, "\u5e73\u6cc9\u5e02": 3},
                "\u5510\u5c71\u5e02": {"\u7389\u7530\u53bf": 1, "\u4e30\u6da6\u533a": 1, "\u8fc1\u5b89\u5e02": 1,
                                       "\u8def\u5317\u533a": 1, "\u6ee6\u53bf": 2},
                "\u79e6\u7687\u5c9b\u5e02": {"\u5317\u6234\u6cb3\u533a": 1, "\u660c\u9ece\u53bf": 1,
                                             "\u629a\u5b81\u533a": 1, "\u6d77\u6e2f\u533a": 1,
                                             "\u5c71\u6d77\u5173\u533a": 1, "\u5362\u9f99\u53bf": 1},
                "\u6ca7\u5dde\u5e02": {"\u6cca\u5934\u5e02": 1, "\u6ca7\u53bf": 1, "\u65b0\u534e\u533a": 1,
                                       "\u4e1c\u5149\u53bf": 1, "\u9752\u53bf": 1, "\u4efb\u4e18\u5e02": 1,
                                       "\u8083\u5b81\u53bf": 1, "\u5434\u6865\u53bf": 1},
                "\u5f20\u5bb6\u53e3\u5e02": {"\u6000\u5b89\u53bf": 1, "\u6000\u6765\u53bf": 3,
                                             "\u4e0b\u82b1\u56ed\u533a": 2, "\u6865\u897f\u533a": 1,
                                             "\u5ba3\u5316\u533a": 1},
                "\u8861\u6c34\u5e02": {"\u67a3\u5f3a\u53bf": 2, "\u6843\u57ce\u533a": 2, "\u666f\u53bf": 2,
                                       "\u6df1\u5dde\u5e02": 2, "\u9976\u9633\u53bf": 1},
                "\u90a2\u53f0\u5e02": {"\u90a2\u53f0\u53bf": 1, "\u6e05\u6cb3\u53bf": 1, "\u4e34\u897f\u53bf": 1,
                                       "\u4e34\u57ce\u53bf": 1, "\u6c99\u6cb3\u5e02": 1, "\u6865\u4e1c\u533a": 1},
                "\u77f3\u5bb6\u5e84\u5e02": {"\u8f9b\u96c6\u5e02": 2, "\u85c1\u57ce\u533a": 2, "\u9ad8\u9091\u53bf": 2,
                                             "\u4e95\u9649\u53bf": 3, "\u664b\u5dde\u5e02": 1, "\u6865\u897f\u533a": 1,
                                             "\u88d5\u534e\u533a": 1, "\u65b0\u534e\u533a": 1, "\u5143\u6c0f\u53bf": 1,
                                             "\u6b63\u5b9a\u53bf": 2}}, "\u5e7f\u4e1c\u7701": {
                "\u8087\u5e86\u5e02": {"\u56db\u4f1a\u5e02": 2, "\u6000\u96c6\u53bf": 1, "\u5e7f\u5b81\u53bf": 1,
                                       "\u9f0e\u6e56\u533a": 3, "\u7aef\u5dde\u533a": 2},
                "\u4f5b\u5c71\u5e02": {"\u4e09\u6c34\u533a": 3, "\u987a\u5fb7\u533a": 5, "\u5357\u6d77\u533a": 3,
                                       "\u7985\u57ce\u533a": 1},
                "\u6df1\u5733\u5e02": {"\u9f99\u5c97\u533a": 3, "\u5b9d\u5b89\u533a": 2, "\u9f99\u534e\u533a": 1,
                                       "\u798f\u7530\u533a": 1, "\u5357\u5c71\u533a": 1, "\u7f57\u6e56\u533a": 1},
                "\u6f6e\u5dde\u5e02": {"\u6f6e\u5b89\u533a": 2, "\u9976\u5e73\u53bf": 1},
                "\u6c55\u5934\u5e02": {"\u6f6e\u9633\u533a": 1, "\u9f99\u6e56\u533a": 1},
                "\u4e1c\u839e\u5e02": {"\u76f4\u5c5e": 15},
                "\u6885\u5dde\u5e02": {"\u5927\u57d4\u53bf": 1, "\u5174\u5b81\u5e02": 1, "\u4e30\u987a\u53bf": 1,
                                       "\u6885\u6c5f\u533a": 1}, "\u4e2d\u5c71\u5e02": {"\u76f4\u5c5e": 7},
                "\u8302\u540d\u5e02": {"\u4fe1\u5b9c\u5e02": 1, "\u9ad8\u5dde\u5e02": 1, "\u5316\u5dde\u5e02": 1,
                                       "\u8302\u5357\u533a": 2},
                "\u6c5f\u95e8\u5e02": {"\u65b0\u4f1a\u533a": 1, "\u6c5f\u6d77\u533a": 1},
                "\u5e7f\u5dde\u5e02": {"\u82b1\u90fd\u533a": 1, "\u5929\u6cb3\u533a": 1, "\u8d8a\u79c0\u533a": 1,
                                       "\u756a\u79ba\u533a": 1, "\u5357\u6c99\u533a": 1},
                "\u60e0\u5dde\u5e02": {"\u60e0\u57ce\u533a": 8, "\u60e0\u4e1c\u53bf": 1, "\u60e0\u9633\u533a": 1,
                                       "\u535a\u7f57\u53bf": 1},
                "\u6e5b\u6c5f\u5e02": {"\u5ec9\u6c5f\u5e02": 2, "\u9042\u6eaa\u53bf": 1, "\u96f7\u5dde\u5e02": 1,
                                       "\u5f90\u95fb\u53bf": 1, "\u971e\u5c71\u533a": 1, "\u9ebb\u7ae0\u533a": 1},
                "\u6e05\u8fdc\u5e02": {"\u82f1\u5fb7\u5e02": 2, "\u6e05\u57ce\u533a": 2},
                "\u97f6\u5173\u5e02": {"\u4e50\u660c\u5e02": 3, "\u59cb\u5174\u53bf": 1, "\u5357\u96c4\u5e02": 1,
                                       "\u6d48\u6c5f\u533a": 1, "\u6b66\u6c5f\u533a": 1},
                "\u4e91\u6d6e\u5e02": {"\u4e91\u5b89\u533a": 1, "\u90c1\u5357\u53bf": 2},
                "\u63ed\u9633\u5e02": {"\u6995\u57ce\u533a": 1, "\u60e0\u6765\u53bf": 1, "\u666e\u5b81\u5e02": 1},
                "\u6c55\u5c3e\u5e02": {"\u6d77\u4e30\u53bf": 1, "\u9646\u4e30\u5e02": 1, "\u57ce\u533a": 1},
                "\u6cb3\u6e90\u5e02": {"\u9f99\u5ddd\u53bf": 1, "\u6e90\u57ce\u533a": 1},
                "\u73e0\u6d77\u5e02": {"\u9999\u6d32\u533a": 5}, "\u9633\u6c5f\u5e02": {"\u9633\u6625\u5e02": 1}},
                "\u5185\u8499\u53e4\u81ea\u6cbb\u533a": {
                    "\u547c\u4f26\u8d1d\u5c14\u5e02": {"\u9102\u4f26\u6625\u81ea\u6cbb\u65d7": 17,
                                                       "\u6839\u6cb3\u5e02": 9, "\u7259\u514b\u77f3\u5e02": 27,
                                                       "\u65b0\u5df4\u5c14\u864e\u5de6\u65d7": 5,
                                                       "\u624e\u5170\u5c6f\u5e02": 5,
                                                       "\u9102\u6e29\u514b\u65cf\u81ea\u6cbb\u65d7": 6,
                                                       "\u6d77\u62c9\u5c14\u533a": 3, "\u6ee1\u6d32\u91cc\u5e02": 2,
                                                       "\u989d\u5c14\u53e4\u7eb3\u5e02": 1,
                                                       "\u83ab\u529b\u8fbe\u74e6\u8fbe\u65a1\u5c14\u65cf\u81ea\u6cbb\u65d7": 4,
                                                       "\u624e\u8d49\u8bfa\u5c14\u533a": 1,
                                                       "\u9648\u5df4\u5c14\u864e\u65d7": 3},
                    "\u901a\u8fbd\u5e02": {"\u79d1\u5c14\u6c81\u5de6\u7ffc\u4e2d\u65d7": 5, "\u5948\u66fc\u65d7": 10,
                                           "\u79d1\u5c14\u6c81\u533a": 8,
                                           "\u79d1\u5c14\u6c81\u5de6\u7ffc\u540e\u65d7": 3,
                                           "\u970d\u6797\u90ed\u52d2\u5e02": 2, "\u5f00\u9c81\u53bf": 2,
                                           "\u5e93\u4f26\u65d7": 2, "\u624e\u9c81\u7279\u65d7": 1},
                    "\u9521\u6797\u90ed\u52d2\u76df": {"\u963f\u5df4\u560e\u65d7": 1, "\u6b63\u9576\u767d\u65d7": 2,
                                                       "\u897f\u4e4c\u73e0\u7a46\u6c81\u65d7": 2,
                                                       "\u6b63\u84dd\u65d7": 1, "\u82cf\u5c3c\u7279\u5de6\u65d7": 1,
                                                       "\u4e8c\u8fde\u6d69\u7279\u5e02": 5,
                                                       "\u82cf\u5c3c\u7279\u53f3\u65d7": 10,
                                                       "\u9521\u6797\u6d69\u7279\u5e02": 1},
                    "\u5174\u5b89\u76df": {"\u963f\u5c14\u5c71\u5e02": 6,
                                           "\u79d1\u5c14\u6c81\u53f3\u7ffc\u4e2d\u65d7": 5,
                                           "\u79d1\u5c14\u6c81\u53f3\u7ffc\u524d\u65d7": 6,
                                           "\u4e4c\u5170\u6d69\u7279\u5e02": 1},
                    "\u5df4\u5f66\u6dd6\u5c14\u5e02": {"\u78f4\u53e3\u53bf": 1, "\u4e4c\u62c9\u7279\u524d\u65d7": 8,
                                                       "\u4e34\u6cb3\u533a": 1, "\u4e94\u539f\u53bf": 2,
                                                       "\u676d\u9526\u540e\u65d7": 1},
                    "\u5305\u5934\u5e02": {"\u4e1c\u6cb3\u533a": 3, "\u767d\u4e91\u9102\u535a\u77ff\u533a": 1,
                                           "\u6606\u90fd\u4ed1\u533a": 4, "\u4e5d\u539f\u533a": 6,
                                           "\u571f\u9ed8\u7279\u53f3\u65d7": 2, "\u56fa\u9633\u53bf": 4,
                                           "\u8fbe\u5c14\u7f55\u8302\u660e\u5b89\u8054\u5408\u65d7": 2},
                    "\u4e4c\u5170\u5bdf\u5e03\u5e02": {"\u5bdf\u54c8\u5c14\u53f3\u7ffc\u540e\u65d7": 8,
                                                       "\u4e30\u9547\u5e02": 3, "\u5316\u5fb7\u53bf": 1,
                                                       "\u96c6\u5b81\u533a": 1, "\u5353\u8d44\u53bf": 9,
                                                       "\u5546\u90fd\u53bf": 1,
                                                       "\u5bdf\u54c8\u5c14\u53f3\u7ffc\u524d\u65d7": 4,
                                                       "\u5174\u548c\u53bf": 1},
                    "\u8d64\u5cf0\u5e02": {"\u963f\u9c81\u79d1\u5c14\u6c81\u65d7": 1, "\u7ea2\u5c71\u533a": 3,
                                           "\u677e\u5c71\u533a": 11, "\u5df4\u6797\u53f3\u65d7": 1,
                                           "\u6556\u6c49\u65d7": 8, "\u514b\u4ec0\u514b\u817e\u65d7": 1,
                                           "\u5df4\u6797\u5de6\u65d7": 1, "\u6797\u897f\u53bf": 1,
                                           "\u5143\u5b9d\u5c71\u533a": 6, "\u5580\u5587\u6c81\u65d7": 2,
                                           "\u5b81\u57ce\u53bf": 3},
                    "\u547c\u548c\u6d69\u7279\u5e02": {"\u571f\u9ed8\u7279\u5de6\u65d7": 2, "\u65b0\u57ce\u533a": 2,
                                                       "\u8d5b\u7f55\u533a": 1},
                    "\u9102\u5c14\u591a\u65af\u5e02": {"\u8fbe\u62c9\u7279\u65d7": 1, "\u4e1c\u80dc\u533a": 1,
                                                       "\u4f0a\u91d1\u970d\u6d1b\u65d7": 1,
                                                       "\u51c6\u683c\u5c14\u65d7": 1, "\u676d\u9526\u65d7": 1,
                                                       "\u9102\u6258\u514b\u65d7": 1},
                    "\u963f\u62c9\u5584\u76df": {"\u989d\u6d4e\u7eb3\u65d7": 1, "\u963f\u62c9\u5584\u5de6\u65d7": 1},
                    "\u4e4c\u6d77\u5e02": {"\u6d77\u52c3\u6e7e\u533a": 2, "\u4e4c\u8fbe\u533a": 1}},
                "\u8fbd\u5b81\u7701": {"\u961c\u65b0\u5e02": {"\u961c\u65b0\u8499\u53e4\u65cf\u81ea\u6cbb\u53bf": 3,
                                                              "\u6d77\u5dde\u533a": 1, "\u6e05\u6cb3\u95e8\u533a": 1,
                                                              "\u65b0\u90b1\u533a": 1, "\u5f70\u6b66\u53bf": 1},
                                       "\u8fbd\u9633\u5e02": {"\u5f13\u957f\u5cad\u533a": 1, "\u706f\u5854\u5e02": 2,
                                                              "\u8fbd\u9633\u53bf": 2, "\u592a\u5b50\u6cb3\u533a": 1},
                                       "\u978d\u5c71\u5e02": {"\u94c1\u4e1c\u533a": 2, "\u94c1\u897f\u533a": 1,
                                                              "\u6d77\u57ce\u5e02": 4, "\u53f0\u5b89\u53bf": 1,
                                                              "\u7acb\u5c71\u533a": 1},
                                       "\u94c1\u5cad\u5e02": {"\u660c\u56fe\u53bf": 5, "\u5f00\u539f\u5e02": 2,
                                                              "\u94c1\u5cad\u53bf": 1, "\u94f6\u5dde\u533a": 1,
                                                              "\u897f\u4e30\u53bf": 1},
                                       "\u4e39\u4e1c\u5e02": {"\u4e1c\u6e2f\u5e02": 3,
                                                              "\u5bbd\u7538\u6ee1\u65cf\u81ea\u6cbb\u53bf": 6,
                                                              "\u632f\u5174\u533a": 2, "\u51e4\u57ce\u5e02": 16,
                                                              "\u632f\u5b89\u533a": 3},
                                       "\u672c\u6eaa\u5e02": {"\u6eaa\u6e56\u533a": 3, "\u5e73\u5c71\u533a": 3,
                                                              "\u672c\u6eaa\u6ee1\u65cf\u81ea\u6cbb\u53bf": 7,
                                                              "\u5357\u82ac\u533a": 3,
                                                              "\u6853\u4ec1\u6ee1\u65cf\u81ea\u6cbb\u53bf": 4,
                                                              "\u660e\u5c71\u533a": 1},
                                       "\u8425\u53e3\u5e02": {"\u9c85\u9c7c\u5708\u533a": 2,
                                                              "\u5927\u77f3\u6865\u5e02": 1, "\u76d6\u5dde\u5e02": 2,
                                                              "\u8001\u8fb9\u533a": 2, "\u7ad9\u524d\u533a": 1},
                                       "\u629a\u987a\u5e02": {"\u6e05\u539f\u6ee1\u65cf\u81ea\u6cbb\u53bf": 4,
                                                              "\u65b0\u629a\u533a": 1, "\u987a\u57ce\u533a": 1,
                                                              "\u671b\u82b1\u533a": 1,
                                                              "\u65b0\u5bbe\u6ee1\u65cf\u81ea\u6cbb\u53bf": 1,
                                                              "\u629a\u987a\u53bf": 1},
                                       "\u5927\u8fde\u5e02": {"\u666e\u5170\u5e97\u533a": 3,
                                                              "\u7518\u4e95\u5b50\u533a": 1, "\u4e2d\u5c71\u533a": 1,
                                                              "\u91d1\u5dde\u533a": 6, "\u5e84\u6cb3\u5e02": 3,
                                                              "\u74e6\u623f\u5e97\u5e02": 3},
                                       "\u6c88\u9633\u5e02": {"\u82cf\u5bb6\u5c6f\u533a": 6, "\u65b0\u6c11\u5e02": 3,
                                                              "\u8fbd\u4e2d\u533a": 1, "\u4e8e\u6d2a\u533a": 3,
                                                              "\u6c88\u6cb3\u533a": 1, "\u6d51\u5357\u533a": 2,
                                                              "\u94c1\u897f\u533a": 1},
                                       "\u671d\u9633\u5e02": {"\u53cc\u5854\u533a": 1, "\u9f99\u57ce\u533a": 1,
                                                              "\u51cc\u6e90\u5e02": 11,
                                                              "\u5580\u5587\u6c81\u5de6\u7ffc\u8499\u53e4\u65cf\u81ea\u6cbb\u53bf": 4,
                                                              "\u5317\u7968\u5e02": 3, "\u5efa\u5e73\u53bf": 4},
                                       "\u9526\u5dde\u5e02": {"\u9ed1\u5c71\u53bf": 5, "\u5317\u9547\u5e02": 3,
                                                              "\u51cc\u6d77\u5e02": 3, "\u51cc\u6cb3\u533a": 1,
                                                              "\u4e49\u53bf": 2, "\u592a\u548c\u533a": 2},
                                       "\u846b\u82a6\u5c9b\u5e02": {"\u5174\u57ce\u5e02": 5, "\u5357\u7968\u533a": 1,
                                                                    "\u8fde\u5c71\u533a": 6, "\u5efa\u660c\u53bf": 6,
                                                                    "\u7ee5\u4e2d\u53bf": 3},
                                       "\u76d8\u9526\u5e02": {"\u76d8\u5c71\u53bf": 1, "\u53cc\u53f0\u5b50\u533a": 1,
                                                              "\u5927\u6d3c\u533a": 1}},
                "\u5b81\u590f\u56de\u65cf\u81ea\u6cbb\u533a": {
                    "\u5434\u5fe0\u5e02": {"\u540c\u5fc3\u53bf": 3, "\u9752\u94dc\u5ce1\u5e02": 2,
                                           "\u7ea2\u5bfa\u5821\u533a": 2, "\u76d0\u6c60\u53bf": 1},
                    "\u77f3\u5634\u5c71\u5e02": {"\u5927\u6b66\u53e3\u533a": 5, "\u60e0\u519c\u533a": 1,
                                                 "\u5e73\u7f57\u53bf": 1},
                    "\u4e2d\u536b\u5e02": {"\u4e2d\u5b81\u53bf": 5, "\u6c99\u5761\u5934\u533a": 6,
                                           "\u6d77\u539f\u53bf": 4},
                    "\u56fa\u539f\u5e02": {"\u539f\u5dde\u533a": 6, "\u6cfe\u6e90\u53bf": 2, "\u5f6d\u9633\u53bf": 1},
                    "\u94f6\u5ddd\u5e02": {"\u6c38\u5b81\u53bf": 1, "\u7075\u6b66\u5e02": 3, "\u8d3a\u5170\u53bf": 1,
                                           "\u91d1\u51e4\u533a": 1}},
                "\u65b0\u7586\u7ef4\u543e\u5c14\u81ea\u6cbb\u533a": {
                    "\u535a\u5c14\u5854\u62c9\u8499\u53e4\u81ea\u6cbb\u5dde": {"\u963f\u62c9\u5c71\u53e3\u5e02": 1,
                                                                               "\u7cbe\u6cb3\u53bf": 1},
                    "\u963f\u514b\u82cf\u5730\u533a": {"\u963f\u514b\u82cf\u5e02": 1, "\u5e93\u8f66\u53bf": 1,
                                                       "\u65b0\u548c\u53bf": 1},
                    "\u514b\u5b5c\u52d2\u82cf\u67ef\u5c14\u514b\u5b5c\u81ea\u6cbb\u5dde": {
                        "\u963f\u56fe\u4ec0\u5e02": 1, "\u963f\u514b\u9676\u53bf": 1},
                    "\u963f\u52d2\u6cf0\u5730\u533a": {"\u963f\u52d2\u6cf0\u5e02": 1, "\u798f\u6d77\u53bf": 1},
                    "\u5580\u4ec0\u5730\u533a": {"\u5df4\u695a\u53bf": 1, "\u5580\u4ec0\u5e02": 1,
                                                 "\u838e\u8f66\u53bf": 1, "\u53f6\u57ce\u53bf": 1,
                                                 "\u82f1\u5409\u6c99\u53bf": 1, "\u6cfd\u666e\u53bf": 1},
                    "\u76f4\u5c5e": {"\u53cc\u6cb3\u5e02": 1, "\u5317\u5c6f\u5e02": 1, "\u77f3\u6cb3\u5b50\u5e02": 1},
                    "\u65b0\u7586\u7ef4\u543e\u5c14\u81ea\u6cbb\u533a": {"\u5317\u5c6f\u5e02": 1},
                    "\u4f0a\u7281\u54c8\u8428\u514b\u81ea\u6cbb\u5dde": {"\u970d\u5c14\u679c\u65af\u5e02": 1,
                                                                         "\u594e\u5c6f\u5e02": 1,
                                                                         "\u5c3c\u52d2\u514b\u53bf": 1,
                                                                         "\u970d\u57ce\u53bf": 1,
                                                                         "\u4f0a\u5b81\u5e02": 1,
                                                                         "\u4f0a\u5b81\u53bf": 1},
                    "\u54c8\u5bc6\u5e02": {"\u4f0a\u5dde\u533a": 1},
                    "\u514b\u62c9\u739b\u4f9d\u5e02": {"\u514b\u62c9\u739b\u4f9d\u533a": 1},
                    "\u5df4\u97f3\u90ed\u695e\u8499\u53e4\u81ea\u6cbb\u5dde": {"\u5e93\u5c14\u52d2\u5e02": 1,
                                                                               "\u8f6e\u53f0\u53bf": 1,
                                                                               "\u548c\u7855\u53bf": 2,
                                                                               "\u7109\u8006\u56de\u65cf\u81ea\u6cbb\u53bf": 1},
                    "\u660c\u5409\u56de\u65cf\u81ea\u6cbb\u5dde": {"\u739b\u7eb3\u65af\u53bf": 1},
                    "\u548c\u7530\u5730\u533a": {"\u58a8\u7389\u53bf": 1, "\u76ae\u5c71\u53bf": 1,
                                                 "\u548c\u7530\u5e02": 1},
                    "\u5410\u9c81\u756a\u5e02": {"\u912f\u5584\u53bf": 3, "\u9ad8\u660c\u533a": 2},
                    "\u5854\u57ce\u5730\u533a": {"\u6c99\u6e7e\u53bf": 1,
                                                 "\u548c\u5e03\u514b\u8d5b\u5c14\u8499\u53e4\u81ea\u6cbb\u53bf": 1},
                    "\u4e4c\u9c81\u6728\u9f50\u5e02": {"\u6c99\u4f9d\u5df4\u514b\u533a": 2}}, "\u9655\u897f\u7701": {
                "\u5b89\u5eb7\u5e02": {"\u6c49\u6ee8\u533a": 2, "\u767d\u6cb3\u53bf": 2, "\u65ec\u9633\u53bf": 3,
                                       "\u7d2b\u9633\u53bf": 4, "\u6c49\u9634\u53bf": 1, "\u77f3\u6cc9\u53bf": 1},
                "\u6986\u6797\u5e02": {"\u6986\u9633\u533a": 1, "\u5b9a\u8fb9\u53bf": 1, "\u9756\u8fb9\u53bf": 1,
                                       "\u7c73\u8102\u53bf": 1, "\u7ee5\u5fb7\u53bf": 1, "\u795e\u6728\u5e02": 2,
                                       "\u6e05\u6da7\u53bf": 1, "\u5434\u5821\u53bf": 1, "\u5b50\u6d32\u53bf": 1},
                "\u54b8\u9633\u5e02": {"\u6c38\u5bff\u53bf": 1, "\u5f6c\u53bf": 1, "\u957f\u6b66\u53bf": 1,
                                       "\u793c\u6cc9\u53bf": 1, "\u4e7e\u53bf": 1, "\u4e09\u539f\u53bf": 1,
                                       "\u6b66\u529f\u53bf": 1, "\u79e6\u90fd\u533a": 1, "\u5174\u5e73\u5e02": 1,
                                       "\u6e2d\u57ce\u533a": 1, "\u6cfe\u9633\u53bf": 1, "\u6768\u9675\u533a": 2},
                "\u6c49\u4e2d\u5e02": {"\u9547\u5df4\u53bf": 1, "\u7565\u9633\u53bf": 2, "\u57ce\u56fa\u53bf": 2,
                                       "\u4f5b\u576a\u53bf": 1, "\u6c49\u53f0\u533a": 1, "\u52c9\u53bf": 1,
                                       "\u5b81\u5f3a\u53bf": 3, "\u897f\u4e61\u53bf": 2, "\u6d0b\u53bf": 1},
                "\u5b9d\u9e21\u5e02": {"\u6e2d\u6ee8\u533a": 2, "\u5c90\u5c71\u53bf": 2, "\u51e4\u53bf": 3,
                                       "\u9648\u4ed3\u533a": 2, "\u9647\u53bf": 1, "\u5343\u9633\u53bf": 1},
                "\u897f\u5b89\u5e02": {"\u957f\u5b89\u533a": 2, "\u672a\u592e\u533a": 1, "\u9120\u9091\u533a": 1,
                                       "\u65b0\u57ce\u533a": 1, "\u960e\u826f\u533a": 1},
                "\u5546\u6d1b\u5e02": {"\u4e39\u51e4\u53bf": 1, "\u5546\u5dde\u533a": 2, "\u5546\u5357\u53bf": 1,
                                       "\u9547\u5b89\u53bf": 1, "\u67de\u6c34\u53bf": 1},
                "\u6e2d\u5357\u5e02": {"\u5927\u8354\u53bf": 2, "\u97e9\u57ce\u5e02": 1, "\u534e\u9634\u5e02": 2,
                                       "\u5408\u9633\u53bf": 1, "\u84b2\u57ce\u53bf": 4, "\u6f7c\u5173\u53bf": 1,
                                       "\u4e34\u6e2d\u533a": 2, "\u6f84\u57ce\u53bf": 1, "\u5bcc\u5e73\u53bf": 1},
                "\u5ef6\u5b89\u5e02": {"\u5bcc\u53bf": 1, "\u7518\u6cc9\u53bf": 1, "\u9ec4\u9675\u53bf": 2,
                                       "\u5b9d\u5854\u533a": 1, "\u5b50\u957f\u53bf": 1}}, "\u6e56\u5317\u7701": {
                "\u5b5d\u611f\u5e02": {"\u5b89\u9646\u5e02": 1, "\u5b5d\u5357\u533a": 5, "\u6c49\u5ddd\u5e02": 1,
                                       "\u5927\u609f\u53bf": 1, "\u5e94\u57ce\u5e02": 1, "\u4e91\u68a6\u53bf": 1},
                "\u6069\u65bd\u571f\u5bb6\u65cf\u82d7\u65cf\u81ea\u6cbb\u5dde": {"\u5df4\u4e1c\u53bf": 1,
                                                                                 "\u6069\u65bd\u5e02": 1,
                                                                                 "\u5efa\u59cb\u53bf": 1,
                                                                                 "\u5229\u5ddd\u5e02": 1},
                "\u9ec4\u77f3\u5e02": {"\u9633\u65b0\u53bf": 3, "\u5927\u51b6\u5e02": 2, "\u4e0b\u9646\u533a": 1},
                "\u54b8\u5b81\u5e02": {"\u8d64\u58c1\u5e02": 2, "\u54b8\u5b89\u533a": 6},
                "\u5b9c\u660c\u5e02": {"\u5f53\u9633\u5e02": 1, "\u4f0d\u5bb6\u5c97\u533a": 1, "\u679d\u6c5f\u5e02": 1},
                "\u9102\u5dde\u5e02": {"\u9102\u57ce\u533a": 3, "\u534e\u5bb9\u533a": 3},
                "\u8944\u9633\u5e02": {"\u8c37\u57ce\u53bf": 1, "\u6a0a\u57ce\u533a": 1, "\u8944\u5dde\u533a": 1,
                                       "\u67a3\u9633\u5e02": 1},
                "\u968f\u5dde\u5e02": {"\u5e7f\u6c34\u5e02": 1, "\u66fe\u90fd\u533a": 1},
                "\u6b66\u6c49\u5e02": {"\u6c5f\u6c49\u533a": 1, "\u6c5f\u5cb8\u533a": 1, "\u4e1c\u897f\u6e56\u533a": 1,
                                       "\u6d2a\u5c71\u533a": 3, "\u6c5f\u590f\u533a": 8, "\u9ec4\u9642\u533a": 2,
                                       "\u6b66\u660c\u533a": 1},
                "\u8346\u5dde\u5e02": {"\u8346\u5dde\u533a": 1, "\u677e\u6ecb\u5e02": 1},
                "\u8346\u95e8\u5e02": {"\u4eac\u5c71\u53bf": 1, "\u4e1c\u5b9d\u533a": 1, "\u949f\u7965\u5e02": 1},
                "\u9ec4\u5188\u5e02": {"\u9ec4\u5dde\u533a": 4, "\u9ebb\u57ce\u5e02": 2, "\u8572\u6625\u53bf": 1,
                                       "\u9ec4\u6885\u53bf": 3, "\u7ea2\u5b89\u53bf": 1, "\u6b66\u7a74\u5e02": 1,
                                       "\u6d60\u6c34\u53bf": 1},
                "\u76f4\u5c5e": {"\u6f5c\u6c5f\u5e02": 1, "\u5929\u95e8\u5e02": 2, "\u4ed9\u6843\u5e02": 1},
                "\u5341\u5830\u5e02": {"\u8305\u7bad\u533a": 1, "\u4e39\u6c5f\u53e3\u5e02": 1}}, "\u4e0a\u6d77\u5e02": {
                "\u76f4\u5c5e": {"\u95f5\u884c\u533a": 1, "\u5609\u5b9a\u533a": 2, "\u91d1\u5c71\u533a": 1,
                                 "\u677e\u6c5f\u533a": 2, "\u9759\u5b89\u533a": 1, "\u5f90\u6c47\u533a": 1,
                                 "\u666e\u9640\u533a": 1}}, "\u56db\u5ddd\u7701": {
                "\u5e7f\u5143\u5e02": {"\u9752\u5ddd\u53bf": 3, "\u671d\u5929\u533a": 2, "\u82cd\u6eaa\u53bf": 1,
                                       "\u5229\u5dde\u533a": 1, "\u5251\u9601\u53bf": 1},
                "\u6210\u90fd\u5e02": {"\u90eb\u90fd\u533a": 5, "\u91d1\u725b\u533a": 2, "\u6b66\u4faf\u533a": 1,
                                       "\u90fd\u6c5f\u5830\u5e02": 4, "\u65b0\u90fd\u533a": 1, "\u6210\u534e\u533a": 1,
                                       "\u53cc\u6d41\u533a": 2, "\u65b0\u6d25\u53bf": 2, "\u7b80\u9633\u5e02": 2,
                                       "\u5f6d\u5dde\u5e02": 1, "\u9752\u767d\u6c5f\u533a": 1},
                "\u5e7f\u5b89\u5e02": {"\u5cb3\u6c60\u53bf": 1, "\u534e\u84e5\u5e02": 1, "\u524d\u950b\u533a": 1,
                                       "\u5e7f\u5b89\u533a": 1, "\u6b66\u80dc\u53bf": 1},
                "\u51c9\u5c71\u5f5d\u65cf\u81ea\u6cbb\u5dde": {"\u5fb7\u660c\u53bf": 4, "\u897f\u660c\u5e02": 3,
                                                               "\u559c\u5fb7\u53bf": 10, "\u8d8a\u897f\u53bf": 9,
                                                               "\u5195\u5b81\u53bf": 1, "\u7518\u6d1b\u53bf": 7},
                "\u5fb7\u9633\u5e02": {"\u65cc\u9633\u533a": 1, "\u5e7f\u6c49\u5e02": 1, "\u7f57\u6c5f\u53bf": 1},
                "\u4e50\u5c71\u5e02": {"\u5ce8\u8fb9\u5f5d\u65cf\u81ea\u6cbb\u53bf": 2, "\u5ce8\u7709\u5c71\u5e02": 4,
                                       "\u5e02\u4e2d\u533a": 1, "\u91d1\u53e3\u6cb3\u533a": 3, "\u6c99\u6e7e\u533a": 4},
                "\u8d44\u9633\u5e02": {"\u96c1\u6c5f\u533a": 2},
                "\u6500\u679d\u82b1\u5e02": {"\u4ec1\u548c\u533a": 5, "\u7c73\u6613\u53bf": 3, "\u76d0\u8fb9\u53bf": 1},
                "\u9042\u5b81\u5e02": {"\u5927\u82f1\u53bf": 1, "\u8239\u5c71\u533a": 1},
                "\u5df4\u4e2d\u5e02": {"\u5df4\u5dde\u533a": 1, "\u5e73\u660c\u53bf": 1},
                "\u7709\u5c71\u5e02": {"\u4e1c\u5761\u533a": 2, "\u5f6d\u5c71\u533a": 1, "\u9752\u795e\u53bf": 1},
                "\u7ef5\u9633\u5e02": {"\u6c5f\u6cb9\u5e02": 3, "\u6daa\u57ce\u533a": 1},
                "\u8fbe\u5dde\u5e02": {"\u5f00\u6c5f\u53bf": 1, "\u5ba3\u6c49\u53bf": 2, "\u6e20\u53bf": 3,
                                       "\u901a\u5ddd\u533a": 1, "\u4e07\u6e90\u5e02": 1, "\u8fbe\u5ddd\u533a": 1},
                "\u5185\u6c5f\u5e02": {"\u9686\u660c\u5e02": 2, "\u5e02\u4e2d\u533a": 1, "\u4e1c\u5174\u533a": 1,
                                       "\u8d44\u4e2d\u53bf": 2},
                "\u5357\u5145\u5e02": {"\u9606\u4e2d\u5e02": 1, "\u5357\u90e8\u53bf": 1, "\u987a\u5e86\u533a": 2,
                                       "\u8425\u5c71\u53bf": 1, "\u84ec\u5b89\u53bf": 1},
                "\u96c5\u5b89\u5e02": {"\u6c49\u6e90\u53bf": 1}, "\u5b9c\u5bbe\u5e02": {"\u7fe0\u5c4f\u533a": 1},
                "\u81ea\u8d21\u5e02": {"\u5927\u5b89\u533a": 1}}, "\u5b89\u5fbd\u7701": {
                "\u5b89\u5e86\u5e02": {"\u6000\u5b81\u53bf": 1, "\u5b9c\u79c0\u533a": 1, "\u5bbf\u677e\u53bf": 1,
                                       "\u6f5c\u5c71\u53bf": 1, "\u592a\u6e56\u53bf": 1, "\u6850\u57ce\u5e02": 1},
                "\u868c\u57e0\u5e02": {"\u9f99\u5b50\u6e56\u533a": 2, "\u56fa\u9547\u53bf": 1},
                "\u4eb3\u5dde\u5e02": {"\u8c2f\u57ce\u533a": 1, "\u6da1\u9633\u53bf": 1},
                "\u5408\u80a5\u5e02": {"\u5de2\u6e56\u5e02": 2, "\u957f\u4e30\u53bf": 2, "\u5305\u6cb3\u533a": 1,
                                       "\u80a5\u4e1c\u53bf": 1, "\u7476\u6d77\u533a": 1, "\u5e90\u6c5f\u53bf": 1},
                "\u6ec1\u5dde\u5e02": {"\u7405\u740a\u533a": 1, "\u5357\u8c2f\u533a": 1, "\u5b9a\u8fdc\u53bf": 1,
                                       "\u5168\u6912\u53bf": 1, "\u660e\u5149\u5e02": 1},
                "\u6c60\u5dde\u5e02": {"\u4e1c\u81f3\u53bf": 1, "\u8d35\u6c60\u533a": 1},
                "\u5bbf\u5dde\u5e02": {"\u7800\u5c71\u53bf": 2, "\u7075\u74a7\u53bf": 1, "\u6cd7\u53bf": 1,
                                       "\u8427\u53bf": 2, "\u57c7\u6865\u533a": 2},
                "\u5ba3\u57ce\u5e02": {"\u5ba3\u5dde\u533a": 1, "\u5e7f\u5fb7\u53bf": 1, "\u7ee9\u6eaa\u53bf": 2,
                                       "\u6cfe\u53bf": 1, "\u5b81\u56fd\u5e02": 1, "\u65cc\u5fb7\u53bf": 1},
                "\u516d\u5b89\u5e02": {"\u970d\u90b1\u53bf": 1, "\u91d1\u5be8\u53bf": 1, "\u8212\u57ce\u53bf": 1,
                                       "\u88d5\u5b89\u533a": 1},
                "\u961c\u9633\u5e02": {"\u988d\u4e1c\u533a": 1, "\u754c\u9996\u5e02": 1, "\u592a\u548c\u53bf": 1,
                                       "\u988d\u4e0a\u53bf": 1},
                "\u6dee\u5357\u5e02": {"\u7530\u5bb6\u5eb5\u533a": 1, "\u5927\u901a\u533a": 1},
                "\u9ec4\u5c71\u5e02": {"\u5c6f\u6eaa\u533a": 1, "\u6b59\u53bf": 2, "\u5fbd\u5dde\u533a": 1,
                                       "\u7941\u95e8\u53bf": 1},
                "\u6dee\u5317\u5e02": {"\u76f8\u5c71\u533a": 1, "\u675c\u96c6\u533a": 1},
                "\u829c\u6e56\u5e02": {"\u65e0\u4e3a\u53bf": 1, "\u5357\u9675\u53bf": 1, "\u7e41\u660c\u53bf": 1,
                                       "\u5f0b\u6c5f\u533a": 1, "\u955c\u6e56\u533a": 1},
                "\u94dc\u9675\u5e02": {"\u4e49\u5b89\u533a": 1, "\u94dc\u5b98\u533a": 1},
                "\u9a6c\u978d\u5c71\u5e02": {"\u82b1\u5c71\u533a": 2, "\u5f53\u6d82\u53bf": 1}}, "\u5c71\u4e1c\u7701": {
                "\u6dc4\u535a\u5e02": {"\u535a\u5c71\u533a": 2, "\u6dc4\u5ddd\u533a": 1, "\u4e34\u6dc4\u533a": 1,
                                       "\u5f20\u5e97\u533a": 1},
                "\u6cf0\u5b89\u5e02": {"\u6cf0\u5c71\u533a": 3, "\u5b81\u9633\u53bf": 1, "\u5cb1\u5cb3\u533a": 2},
                "\u6ee8\u5dde\u5e02": {"\u6ee8\u57ce\u533a": 1, "\u535a\u5174\u53bf": 1, "\u9633\u4fe1\u53bf": 1},
                "\u6f4d\u574a\u5e02": {"\u660c\u4e50\u53bf": 1, "\u9ad8\u5bc6\u5e02": 1, "\u9752\u5dde\u5e02": 1,
                                       "\u6f4d\u57ce\u533a": 1, "\u8bf8\u57ce\u5e02": 1},
                "\u4e34\u6c82\u5e02": {"\u5170\u9675\u53bf": 1, "\u8d39\u53bf": 1, "\u8392\u5357\u53bf": 2,
                                       "\u5170\u5c71\u533a": 1, "\u5e73\u9091\u53bf": 1, "\u90ef\u57ce\u53bf": 1,
                                       "\u6cb3\u4e1c\u533a": 1, "\u6c82\u5357\u53bf": 1, "\u6c82\u6c34\u53bf": 1},
                "\u83b1\u829c\u5e02": {"\u83b1\u57ce\u533a": 4},
                "\u83cf\u6cfd\u5e02": {"\u66f9\u53bf": 1, "\u4e1c\u660e\u53bf": 1, "\u5b9a\u9676\u533a": 1,
                                       "\u7261\u4e39\u533a": 1, "\u9104\u57ce\u53bf": 1, "\u5de8\u91ce\u53bf": 1,
                                       "\u90d3\u57ce\u53bf": 1},
                "\u5fb7\u5dde\u5e02": {"\u5fb7\u57ce\u533a": 2, "\u9675\u57ce\u533a": 1, "\u4e34\u9091\u53bf": 1,
                                       "\u5e73\u539f\u53bf": 2, "\u79b9\u57ce\u5e02": 2, "\u9f50\u6cb3\u53bf": 1},
                "\u4e1c\u8425\u5e02": {"\u4e1c\u8425\u533a": 2, "\u5229\u6d25\u53bf": 1},
                "\u70df\u53f0\u5e02": {"\u6d77\u9633\u5e02": 2, "\u83b1\u9633\u5e02": 1, "\u725f\u5e73\u533a": 1,
                                       "\u6816\u971e\u5e02": 2, "\u829d\u7f58\u533a": 1, "\u83b1\u5c71\u533a": 1,
                                       "\u9f99\u53e3\u5e02": 1, "\u84ec\u83b1\u5e02": 1, "\u798f\u5c71\u533a": 1},
                "\u6d4e\u5357\u5e02": {"\u5929\u6865\u533a": 2, "\u69d0\u836b\u533a": 1, "\u5546\u6cb3\u53bf": 1,
                                       "\u7ae0\u4e18\u533a": 1},
                "\u6d4e\u5b81\u5e02": {"\u4efb\u57ce\u533a": 1, "\u5609\u7965\u53bf": 1, "\u6881\u5c71\u53bf": 1,
                                       "\u6cd7\u6c34\u53bf": 1, "\u66f2\u961c\u5e02": 2, "\u5156\u5dde\u533a": 1,
                                       "\u90b9\u57ce\u5e02": 1},
                "\u65e5\u7167\u5e02": {"\u8392\u53bf": 1, "\u4e1c\u6e2f\u533a": 1, "\u4e94\u83b2\u53bf": 1},
                "\u9752\u5c9b\u5e02": {"\u5373\u58a8\u5e02": 2, "\u80f6\u5dde\u5e02": 1, "\u83b1\u897f\u5e02": 2,
                                       "\u5e73\u5ea6\u5e02": 1, "\u5e02\u5357\u533a": 1, "\u674e\u6ca7\u533a": 1},
                "\u5a01\u6d77\u5e02": {"\u8363\u6210\u5e02": 1, "\u4e73\u5c71\u5e02": 1, "\u6587\u767b\u533a": 2,
                                       "\u73af\u7fe0\u533a": 2},
                "\u67a3\u5e84\u5e02": {"\u6ed5\u5dde\u5e02": 2, "\u859b\u57ce\u533a": 2, "\u5e02\u4e2d\u533a": 1},
                "\u804a\u57ce\u5e02": {"\u4e1c\u660c\u5e9c\u533a": 1, "\u4e34\u6e05\u5e02": 1,
                                       "\u9633\u8c37\u53bf": 1}}, "\u8d35\u5dde\u7701": {
                "\u9ed4\u4e1c\u5357\u82d7\u65cf\u4f97\u65cf\u81ea\u6cbb\u5dde": {"\u65bd\u79c9\u53bf": 1,
                                                                                 "\u51ef\u91cc\u5e02": 2,
                                                                                 "\u4ece\u6c5f\u53bf": 1,
                                                                                 "\u4e09\u7a57\u53bf": 1,
                                                                                 "\u6995\u6c5f\u53bf": 1,
                                                                                 "\u9547\u8fdc\u53bf": 1},
                "\u5b89\u987a\u5e02": {"\u897f\u79c0\u533a": 2,
                                       "\u5173\u5cad\u5e03\u4f9d\u65cf\u82d7\u65cf\u81ea\u6cbb\u53bf": 1,
                                       "\u5e73\u575d\u533a": 3, "\u666e\u5b9a\u53bf": 1},
                "\u516d\u76d8\u6c34\u5e02": {"\u6c34\u57ce\u53bf": 7, "\u76d8\u5dde\u5e02": 17,
                                             "\u516d\u679d\u7279\u533a": 3, "\u949f\u5c71\u533a": 2},
                "\u9ed4\u897f\u5357\u5e03\u4f9d\u65cf\u82d7\u65cf\u81ea\u6cbb\u5dde": {"\u5174\u4e49\u5e02": 5,
                                                                                       "\u518c\u4ea8\u53bf": 1,
                                                                                       "\u666e\u5b89\u53bf": 1},
                "\u6bd5\u8282\u5e02": {"\u5927\u65b9\u53bf": 1, "\u7ec7\u91d1\u53bf": 1, "\u7eb3\u96cd\u53bf": 1,
                                       "\u5a01\u5b81\u5f5d\u65cf\u56de\u65cf\u82d7\u65cf\u81ea\u6cbb\u53bf": 3},
                "\u8d35\u9633\u5e02": {"\u4e4c\u5f53\u533a": 3, "\u5f00\u9633\u53bf": 2, "\u5357\u660e\u533a": 2,
                                       "\u89c2\u5c71\u6e56\u533a": 1, "\u606f\u70fd\u53bf": 1, "\u4fee\u6587\u53bf": 1},
                "\u9ed4\u5357\u5e03\u4f9d\u65cf\u82d7\u65cf\u81ea\u6cbb\u5dde": {"\u8d35\u5b9a\u53bf": 4,
                                                                                 "\u9f99\u91cc\u53bf": 1,
                                                                                 "\u90fd\u5300\u5e02": 2,
                                                                                 "\u4e09\u90fd\u6c34\u65cf\u81ea\u6cbb\u53bf": 1,
                                                                                 "\u72ec\u5c71\u53bf": 2,
                                                                                 "\u798f\u6cc9\u5e02": 1},
                "\u94dc\u4ec1\u5e02": {"\u78a7\u6c5f\u533a": 1, "\u7389\u5c4f\u4f97\u65cf\u81ea\u6cbb\u53bf": 2},
                "\u9075\u4e49\u5e02": {"\u7ea2\u82b1\u5c97\u533a": 2, "\u6c47\u5ddd\u533a": 1, "\u6850\u6893\u53bf": 2,
                                       "\u64ad\u5dde\u533a": 1}}, "\u6d59\u6c5f\u7701": {
                "\u6e29\u5dde\u5e02": {"\u5e73\u9633\u53bf": 1, "\u82cd\u5357\u53bf": 1, "\u4e50\u6e05\u5e02": 3,
                                       "\u745e\u5b89\u5e02": 1, "\u9e7f\u57ce\u533a": 1, "\u6c38\u5609\u53bf": 1,
                                       "\u74ef\u6d77\u533a": 1},
                "\u7ecd\u5174\u5e02": {"\u4e0a\u865e\u533a": 2, "\u8d8a\u57ce\u533a": 2, "\u8bf8\u66a8\u5e02": 1},
                "\u6e56\u5dde\u5e02": {"\u957f\u5174\u53bf": 2, "\u5fb7\u6e05\u53bf": 2, "\u5434\u5174\u533a": 1},
                "\u8862\u5dde\u5e02": {"\u5e38\u5c71\u53bf": 1, "\u6c5f\u5c71\u5e02": 1, "\u5f00\u5316\u53bf": 1,
                                       "\u9f99\u6e38\u53bf": 1, "\u67ef\u57ce\u533a": 1},
                "\u5b81\u6ce2\u5e02": {"\u4f59\u59da\u5e02": 2, "\u5949\u5316\u533a": 1, "\u6d77\u66d9\u533a": 1,
                                       "\u5b81\u6d77\u53bf": 1, "\u6c5f\u5317\u533a": 1},
                "\u5609\u5174\u5e02": {"\u5609\u5584\u53bf": 2, "\u5357\u6e56\u533a": 2, "\u6d77\u5b81\u5e02": 2,
                                       "\u6850\u4e61\u5e02": 1},
                "\u676d\u5dde\u5e02": {"\u4f59\u676d\u533a": 1, "\u6c5f\u5e72\u533a": 1, "\u4e0a\u57ce\u533a": 1},
                "\u91d1\u534e\u5e02": {"\u5a7a\u57ce\u533a": 1, "\u5170\u6eaa\u5e02": 1, "\u6c38\u5eb7\u5e02": 2,
                                       "\u91d1\u4e1c\u533a": 1, "\u6b66\u4e49\u53bf": 2, "\u4e49\u4e4c\u5e02": 1},
                "\u4e3d\u6c34\u5e02": {"\u7f19\u4e91\u53bf": 2, "\u9752\u7530\u53bf": 1, "\u83b2\u90fd\u533a": 1},
                "\u53f0\u5dde\u5e02": {"\u4e09\u95e8\u53bf": 1, "\u9ec4\u5ca9\u533a": 1, "\u4e34\u6d77\u5e02": 1,
                                       "\u6e29\u5cad\u5e02": 1}}, "\u7518\u8083\u7701": {
                "\u5e73\u51c9\u5e02": {"\u534e\u4ead\u53bf": 1, "\u6cfe\u5ddd\u53bf": 1, "\u5d06\u5cd2\u533a": 4,
                                       "\u5d07\u4fe1\u53bf": 1},
                "\u767d\u94f6\u5e02": {"\u767d\u94f6\u533a": 3, "\u666f\u6cf0\u53bf": 4, "\u5e73\u5ddd\u533a": 1,
                                       "\u9756\u8fdc\u53bf": 4},
                "\u5170\u5dde\u5e02": {"\u897f\u56fa\u533a": 4, "\u768b\u5170\u53bf": 5, "\u6986\u4e2d\u53bf": 4,
                                       "\u7ea2\u53e4\u533a": 1, "\u4e03\u91cc\u6cb3\u533a": 1, "\u6c38\u767b\u53bf": 4,
                                       "\u57ce\u5173\u533a": 2}, "\u5e86\u9633\u5e02": {"\u5b81\u53bf": 1},
                "\u6b66\u5a01\u5e02": {"\u5929\u795d\u85cf\u65cf\u81ea\u6cbb\u53bf": 2, "\u53e4\u6d6a\u53bf": 3,
                                       "\u51c9\u5dde\u533a": 5},
                "\u9152\u6cc9\u5e02": {"\u6566\u714c\u5e02": 1, "\u74dc\u5dde\u53bf": 6, "\u7389\u95e8\u5e02": 2,
                                       "\u8083\u5dde\u533a": 4},
                "\u5b9a\u897f\u5e02": {"\u5b89\u5b9a\u533a": 3, "\u9647\u897f\u53bf": 2, "\u5cb7\u53bf": 1,
                                       "\u901a\u6e2d\u53bf": 1, "\u6e2d\u6e90\u53bf": 1, "\u6f33\u53bf": 1},
                "\u5f20\u6396\u5e02": {"\u9ad8\u53f0\u53bf": 3, "\u8083\u5357\u88d5\u56fa\u65cf\u81ea\u6cbb\u53bf": 2,
                                       "\u4e34\u6cfd\u53bf": 2, "\u6c11\u4e50\u53bf": 1, "\u7518\u5dde\u533a": 3,
                                       "\u5c71\u4e39\u53bf": 1},
                "\u5929\u6c34\u5e02": {"\u7518\u8c37\u53bf": 2, "\u6b66\u5c71\u53bf": 4, "\u9ea6\u79ef\u533a": 6,
                                       "\u79e6\u5b89\u53bf": 1, "\u6e05\u6c34\u53bf": 1,
                                       "\u5f20\u5bb6\u5ddd\u56de\u65cf\u81ea\u6cbb\u53bf": 1},
                "\u9647\u5357\u5e02": {"\u5b95\u660c\u53bf": 1, "\u4e24\u5f53\u53bf": 2, "\u5fbd\u53bf": 1,
                                       "\u6b66\u90fd\u533a": 1}, "\u5609\u5cea\u5173\u5e02": {"\u76f4\u5c5e": 3},
                "\u91d1\u660c\u5e02": {"\u6c38\u660c\u53bf": 2, "\u91d1\u5ddd\u533a": 1}},
                "\u5e7f\u897f\u58ee\u65cf\u81ea\u6cbb\u533a": {
                    "\u7389\u6797\u5e02": {"\u535a\u767d\u53bf": 2, "\u5317\u6d41\u5e02": 1, "\u9646\u5ddd\u53bf": 1,
                                           "\u5bb9\u53bf": 1, "\u5174\u4e1a\u53bf": 1, "\u7389\u5dde\u533a": 1},
                    "\u5317\u6d77\u5e02": {"\u6d77\u57ce\u533a": 1, "\u5408\u6d66\u53bf": 1},
                    "\u767e\u8272\u5e02": {"\u53f3\u6c5f\u533a": 1, "\u9756\u897f\u5e02": 1, "\u5e73\u679c\u53bf": 1,
                                           "\u5fb7\u4fdd\u53bf": 1, "\u7530\u4e1c\u53bf": 1, "\u7530\u6797\u53bf": 1,
                                           "\u7530\u9633\u53bf": 1},
                    "\u68a7\u5dde\u5e02": {"\u5c91\u6eaa\u5e02": 1, "\u85e4\u53bf": 1, "\u9f99\u5729\u533a": 1,
                                           "\u957f\u6d32\u533a": 1},
                    "\u5d07\u5de6\u5e02": {"\u6c5f\u5dde\u533a": 2, "\u6276\u7ee5\u53bf": 2, "\u5b81\u660e\u53bf": 2,
                                           "\u51ed\u7965\u5e02": 1},
                    "\u9632\u57ce\u6e2f\u5e02": {"\u9632\u57ce\u533a": 1},
                    "\u8d3a\u5dde\u5e02": {"\u5bcc\u5ddd\u7476\u65cf\u81ea\u6cbb\u53bf": 1, "\u5e73\u6842\u533a": 1,
                                           "\u949f\u5c71\u53bf": 1},
                    "\u8d35\u6e2f\u5e02": {"\u6842\u5e73\u5e02": 1, "\u6e2f\u5317\u533a": 1, "\u5e73\u5357\u53bf": 1},
                    "\u6842\u6797\u5e02": {"\u53e0\u5f69\u533a": 1, "\u606d\u57ce\u7476\u65cf\u81ea\u6cbb\u53bf": 1,
                                           "\u7075\u5ddd\u53bf": 1, "\u8c61\u5c71\u533a": 1, "\u5168\u5dde\u53bf": 1,
                                           "\u5174\u5b89\u53bf": 1, "\u6c38\u798f\u53bf": 1, "\u9633\u6714\u53bf": 1},
                    "\u5357\u5b81\u5e02": {"\u9686\u5b89\u53bf": 1, "\u5bbe\u9633\u53bf": 2, "\u9752\u79c0\u533a": 1,
                                           "\u897f\u4e61\u5858\u533a": 2},
                    "\u6cb3\u6c60\u5e02": {"\u91d1\u57ce\u6c5f\u533a": 1, "\u5357\u4e39\u53bf": 1,
                                           "\u7f57\u57ce\u4eeb\u4f6c\u65cf\u81ea\u6cbb\u53bf": 1,
                                           "\u5b9c\u5dde\u533a": 1},
                    "\u67f3\u5dde\u5e02": {"\u9e7f\u5be8\u53bf": 2, "\u67f3\u5357\u533a": 1, "\u878d\u5b89\u53bf": 1,
                                           "\u878d\u6c34\u82d7\u65cf\u81ea\u6cbb\u53bf": 1,
                                           "\u4e09\u6c5f\u4f97\u65cf\u81ea\u6cbb\u53bf": 1, "\u67f3\u6c5f\u533a": 1},
                    "\u94a6\u5dde\u5e02": {"\u94a6\u5357\u533a": 1}, "\u6765\u5bbe\u5e02": {"\u5174\u5bbe\u533a": 2}},
                "\u5929\u6d25\u5e02": {
                    "\u76f4\u5c5e": {"\u5b9d\u577b\u533a": 2, "\u6b66\u6e05\u533a": 4, "\u6ee8\u6d77\u65b0\u533a": 4,
                                     "\u9759\u6d77\u533a": 1, "\u84df\u5dde\u533a": 3, "\u4e1c\u4e3d\u533a": 1,
                                     "\u5b81\u6cb3\u533a": 1, "\u6cb3\u5317\u533a": 2, "\u897f\u9752\u533a": 2,
                                     "\u7ea2\u6865\u533a": 1}}, "\u798f\u5efa\u7701": {
                "\u9f99\u5ca9\u5e02": {"\u957f\u6c40\u53bf": 1, "\u8fde\u57ce\u53bf": 1, "\u65b0\u7f57\u533a": 1,
                                       "\u4e0a\u676d\u53bf": 1, "\u6c38\u5b9a\u533a": 1, "\u6f33\u5e73\u5e02": 1},
                "\u5b81\u5fb7\u5e02": {"\u798f\u5b89\u5e02": 1, "\u798f\u9f0e\u5e02": 2, "\u53e4\u7530\u53bf": 2,
                                       "\u8549\u57ce\u533a": 1, "\u971e\u6d66\u53bf": 1},
                "\u798f\u5dde\u5e02": {"\u798f\u6e05\u5e02": 1, "\u4ed3\u5c71\u533a": 1, "\u664b\u5b89\u533a": 1,
                                       "\u8fde\u6c5f\u53bf": 1, "\u7f57\u6e90\u53bf": 1, "\u95fd\u6e05\u53bf": 1,
                                       "\u6c38\u6cf0\u53bf": 1},
                "\u6f33\u5dde\u5e02": {"\u9f99\u6587\u533a": 1, "\u9f99\u6d77\u5e02": 2, "\u5357\u9756\u53bf": 2,
                                       "\u4e91\u9704\u53bf": 1, "\u6f33\u6d66\u53bf": 1, "\u8bcf\u5b89\u53bf": 1},
                "\u5357\u5e73\u5e02": {"\u5149\u6cfd\u53bf": 1, "\u5efa\u74ef\u5e02": 2, "\u5efa\u9633\u533a": 2,
                                       "\u5ef6\u5e73\u533a": 2, "\u987a\u660c\u53bf": 1, "\u90b5\u6b66\u5e02": 1,
                                       "\u6b66\u5937\u5c71\u5e02": 2},
                "\u8386\u7530\u5e02": {"\u6db5\u6c5f\u533a": 1, "\u79c0\u5c7f\u533a": 1, "\u4ed9\u6e38\u53bf": 1},
                "\u6cc9\u5dde\u5e02": {"\u60e0\u5b89\u53bf": 1, "\u664b\u6c5f\u5e02": 1, "\u4e30\u6cfd\u533a": 1},
                "\u4e09\u660e\u5e02": {"\u5efa\u5b81\u53bf": 1, "\u5c06\u4e50\u53bf": 1, "\u6c99\u53bf": 1,
                                       "\u4e09\u5143\u533a": 1, "\u6cf0\u5b81\u53bf": 1, "\u6c38\u5b89\u5e02": 1,
                                       "\u5c24\u6eaa\u53bf": 1},
                "\u53a6\u95e8\u5e02": {"\u96c6\u7f8e\u533a": 1, "\u601d\u660e\u533a": 1}}, "\u9752\u6d77\u7701": {
                "\u6d77\u897f\u8499\u53e4\u65cf\u85cf\u65cf\u81ea\u6cbb\u5dde": {"\u5fb7\u4ee4\u54c8\u5e02": 1,
                                                                                 "\u683c\u5c14\u6728\u5e02": 2,
                                                                                 "\u6d77\u897f\u8499\u53e4\u65cf\u85cf\u65cf\u81ea\u6cbb\u5dde\u76f4\u8f96": 2,
                                                                                 "\u4e4c\u5170\u53bf": 2},
                "\u897f\u5b81\u5e02": {"\u5927\u901a\u56de\u65cf\u571f\u65cf\u81ea\u6cbb\u53bf": 1,
                                       "\u6e5f\u6e90\u53bf": 1, "\u57ce\u4e1c\u533a": 1},
                "\u6d77\u4e1c\u5e02": {"\u5e73\u5b89\u533a": 2, "\u4e50\u90fd\u533a": 2,
                                       "\u6c11\u548c\u56de\u65cf\u571f\u65cf\u81ea\u6cbb\u53bf": 1},
                "\u6d77\u5317\u85cf\u65cf\u81ea\u6cbb\u5dde": {"\u95e8\u6e90\u56de\u65cf\u81ea\u6cbb\u53bf": 1,
                                                               "\u6d77\u664f\u53bf": 1, "\u521a\u5bdf\u53bf": 2}},
                "\u897f\u85cf\u81ea\u6cbb\u533a": {
                    "\u62c9\u8428\u5e02": {"\u5806\u9f99\u5fb7\u5e86\u533a": 1, "\u66f2\u6c34\u53bf": 1},
                    "\u90a3\u66f2\u5730\u533a": {"\u90a3\u66f2\u53bf": 1},
                    "\u65e5\u5580\u5219\u5e02": {"\u6851\u73e0\u5b5c\u533a": 1}}}
    elif type == 'station':
        name = request.POST.get('station')
        lines = list(Timetable.objects.filter(station=name).order_by('leavetime').values_list('line', flat=True))
        timetable, stations_line, stations_data, stations_locations = {}, {}, {}, {}
        for item in Timetable.objects.filter(line__in=lines).values_list('line', 'station', 'order', 'arrivedate',
                                                                         'arrivetime', 'leavedate', 'leavetime',
                                                                         'staytime'):
            line, station, order, arrivedate, arrivetime, leavedate, leavetime, staytime = item
            if station not in stations_line:
                stations_line[station] = {}
            stations_line[station][line] = item[2:]
            if line not in timetable:
                timetable[line] = [None, None, None, None, None, 1]
            if order == 1:
                timetable[line][:2] = [station, station]
            elif order > timetable[line][-1]:
                timetable[line][1] = station
                timetable[line][-1] = order
            if station == name:
                timetable[line][2:5] = [str(arrivetime)[:-3], str(leavetime)[:-3], staytime]
        for station, station_data in stations_line.items():
            if station != name:
                stations_data[station] = [0, 10000]
                for line, line_data in station_data.items():
                    station_line = stations_line[name][line]
                    a, b = [station_line, line_data] if line_data[0] < station_line[0] else [line_data, station_line]
                    runtime = round((datetime(1970, 1, a[1], a[2].hour, a[2].minute, 0) - datetime(1970, 1, b[3],
                                                                                                   b[4].hour,
                                                                                                   b[4].minute,
                                                                                                   0)).total_seconds() / 3600,
                                    1)
                    if runtime < stations_data[station][1]:
                        stations_data[station][1] = runtime
                    stations_data[station][0] += 1
        for item in Station.objects.filter(cn__in=[station for station in stations_data] + [name]).values_list('x', 'y',
                                                                                                               'cn',
                                                                                                               'province',
                                                                                                               'city',
                                                                                                               'county'):
            stations_locations[item[2]] = list(item)
        timetable = sorted([[k] + v[:-1] for k, v in timetable.items()], key=lambda x: x[-2])
        stations = [stations_locations[k] + v for k, v in stations_data.items()]
        stations.insert(0, stations_locations[name] + [0, 0])
        data = {'车次': timetable, '车站': stations}
    elif type == 'line':
        name = request.POST.get('line')
        stations = []
        for item in Timetable.objects.filter(line=name).order_by('order').values_list('order', 'station', 'arrivedate',
                                                                                      'arrivetime', 'leavedate',
                                                                                      'leavetime',
                                                                                      'staytime'):
            item, item[3], item[5] = list(item), str(item[3])[:-3], str(item[5])[:-3]
            data.append(item)
            stations.append(item[1])
        for item in Station.objects.filter(cn__in=stations).values_list('cn', 'x', 'y', 'province', 'city', 'county'):
            n = stations.index(item[0])
            data[n] = list(item[1:]) + data[n]
    elif type == 'search':
        data = search(request.POST.get('key'))[1]
    elif type == 'luck':
        data = luck()
    else:
        data = 'ERROR'
    return HttpResponse(json.dumps(data), content_type='application/json')


def log(request):
    return render(request, 'log.html')
