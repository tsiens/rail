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


def ticket(ticket):
    start, arrive, date = ticket.split('|')
    start = Station.objects.get(cn=start).en
    arrive = Station.objects.get(cn=arrive).en
    ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT'
    print(ticket_url % (date, start, arrive))
    get = requests.get(ticket_url % (date, start, arrive), verify=False).json()
    if not get:
        return []
    data = []
    en = {}
    for line in get.get('data', {}).get('result', []):
        line = line.split('|')
        code, name, sf, zd, cf, dd = line[2:8]
        cftime, ddtime, ls = line[8:11]
        if cf not in en:
            en[cf] = Station.objects.get(en=cf).cn
        if dd not in en:
            en[dd] = Station.objects.get(en=dd).cn
        sw, yd, ed, gr, rw, dw, yw, rz, yz, wz = line[32], line[31], line[30], line[21], line[23], line[33], line[28], \
                                                 line[24], line[29], line[26]
        data.append([name, en[cf], en[dd], cftime, ddtime, ls, sw, yd, ed, gr, rw, dw, yw, rz, yz, wz])
    return data


def station_src(station):
    url = 'https://wapbaike.baidu.com/item/%s站'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 7.0; zh-CN; SM-G9300 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.89 UCBrowser/11.5.6.946 Mobile Safari/537.36'}
    src = pq(requests.get(url % station, headers=headers).text)('#J-summary-img').attr('data-src')
    return src