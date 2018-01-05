from web.models import *
import requests
from pyquery import PyQuery as pq
def station(station):
    data = []
    for row in Timetable.objects.filter(station=station).order_by('leavetime'):
        line, arrivetime, leavetime, staytime = row.line, str(row.arrivetime), str(row.leavetime), row.staytime
        staytime = [staytime, '终', '始'][staytime if staytime in [-2, -1] else 0]
        if staytime == '始': arrivetime = '-' * 11
        if staytime == '终': arrivetime = '-' * 11
        data.append([line, arrivetime, leavetime, staytime])
    return data


def line(line):
    data = []
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
    return data

def station_src(station):
    url = 'https://wapbaike.baidu.com/item/%s站'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 7.0; zh-CN; SM-G9300 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.89 UCBrowser/11.5.6.946 Mobile Safari/537.36'}
    src = pq(requests.get(url % station, headers=headers).text)('#J-summary-img').attr('data-src')
    return src
