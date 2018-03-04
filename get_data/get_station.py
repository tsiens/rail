import os
import re
import sys

from pyquery import PyQuery as pq

# encoding='utf-8'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.config import *


def get_station():
    stations_cn, stations_en = stations_lines()[:2]
    get = re.findall('@[^@]+', requests.get(get_station_url, verify=False).text)
    data = []
    for station in get:
        cn, en = station.split('|')[1:3]
        if cn not in stations_cn:
            data.append((cn, en))
            stations_cn[cn], stations_cn[en] = en, cn
            log('%s 插入 %s 站' % (datetime.now().strftime('%H:%M:%S'), cn))
    mysql.execute(("INSERT INTO %s VALUE (null,%%s,%%s,null,null,null,null,null,null,null,null)" % station_table, data))
    # id 站名 代码 经度 维度 省 市 县 时间 图片 图片时间


def get_location():
    data = []
    stations_old, stations_now = mysql.execute(
        "SELECT cn FROM %s " % station_table, "SELECT DISTINCT station FROM %s " % timetable_table)
    for station in set(stations_now) - set(stations_old):
        data.append((station[0]))
        log('%s 插入 %s 站' % (datetime.now().strftime('%H:%M:%S'), station[0]))
    mysql.execute(
        ("INSERT INTO %s VALUE (null,%%s,null,null,null,null,null,null,null,null,null)" % station_table, data))
    stations = [station[0] for station in mysql.execute(
        "SELECT cn FROM %s WHERE cn in (SELECT station FROM %s) and ((x=125 and y=30) or (x IS NULL and y IS NULL)) and (date IS NULL or date<'%s')" % (
            station_table, timetable_table, today))]
    global sqls
    sqls = []
    rs = threadpool.makeRequests(get_location_thread, stations)
    [pool.putRequest(r) for r in rs]
    pool.wait()
    mysql.execute(*sqls)


def get_location_thread(station):
    def get_amap(city):
        get = getjson(amap_url % (station, city, amap_sak))
        for row in get.get('pois', []):
            if station + '站' in row['name']:
                location = row['location'].split(',')
                province = row.get('pname', '')
                city = row.get('cityname', '')
                county = row.get('adname', '')
                get = getjson(amap_to_baidu % (location[0], location[1], baidu_sak))
                x = round(get['result'][0]['x'], 6)
                y = round(get['result'][0]['y'], 6)
                return [x, y, province, city, county]
        return None

    def get_baidu(province, city, county):
        get = getjson(baidu_url % (station, city if city else '北京', baidu_sak))
        for row in get.get('results', []):
            if station + '站' in row['name']:
                return [row['location']['lng'], row['location']['lat'], province, city, county]
        return None

    global sqls
    sqls = []
    station = station.replace(' ', '')
    location = get_amap('全国')
    if location:
        x, y, province, city, county = location
    else:
        try:
            code = getjson(geogv_url1 % station)['data'][0][0]
            info = getjson(geogv_url2 % code)['location'].split(' ')
            province, city = info[:2]
            provinces = ['重庆市', '北京市', '上海市', '天津市']  # 直辖市
            citys = ['东莞市', '中山市', '三沙市', '儋州市', '嘉峪关市']  # 直筒子市
            countys = [
                '济源市',  # 河南
                '仙桃市', '潜江市', '天门市', '神农架林区',  # 湖北
                '五指山市', '文昌市', '琼海市', '万宁市', '东方市', '定安县', '屯昌县', '澄迈县', '临高县', '琼中黎族苗族自治县', '保亭黎族苗族自治县', '白沙黎族自治县',
                '昌江黎族自治县', '乐东黎族自治县', '陵水黎族自治县',
                # 海南
                '石河子市', '阿拉尔市', '图木舒克市', '五家渠市', '北屯市', '铁门关市', '双河市', '可克达拉市', '昆玉市',  # 新疆
            ]  # 省直管
            if province in provinces:
                county, city = city, province + '属'
            elif city in citys:
                county = city + '属'
            elif city in countys:
                city = province + '属'
            else:
                county = info[2]
        except:
            province, city, county = None, None, None
    for location in [get_amap(city), get_baidu(province, city, county)]:
        if location:
            x, y, province, city, county = location
            break
        x, y = 125, 30

    log('查询 %s 站 [%s,%s] %s %s %s' % (station, x, y, province, city, county))
    lock.acquire()
    sqls.append("UPDATE %s SET x='%s',y='%s',province='%s',city='%s',county='%s',date='%s' WHERE cn='%s'" % (
        station_table, x, y, province, city, county, today, station))
    if len(sqls) == 10:
        mysql.execute(*sqls)
        sqls = []
    lock.release()


def get_img():
    stations = [station[0] for station in mysql.execute(
        "SELECT cn FROM %s WHERE cn in (SELECT DISTINCT station FROM %s) and (image_date IS NULL or image_date<'%s')" % (
            station_table, timetable_table, today - timedelta(days=100)))]
    global sqls
    sqls = []
    rs = threadpool.makeRequests(get_img_thread, stations[:100])
    [pool.putRequest(r) for r in rs]
    pool.wait()
    mysql.execute(*sqls)


def get_img_thread(station):
    try:
        src = None
        url = pq(requests.get(wiki_url + '/wiki/%s站' % station, headers=headers, timeout=5).text)(
            '.vcard [colspan="2"] a')
        if url and 'Missing' not in str(url) and 'No' not in str(url):
            src = pq(requests.get(wiki_url + url.attr('href'), headers=headers, timeout=5).text)('.fullMedia a').attr(
                'href')
        test = len(src)
    except:
        src = pq(requests.get(baike_url % station, headers=headers).text)('#J-summary-img').attr('data-src')
        if src:
            src = re.findall(r'src=(.+)', src)[0]
    lock.acquire()
    global sqls
    if src:
        qiniuyun.fetch(src, 'station_img/%s.jpg' % station)
        log('图片 %s 站' % station)
    else:
        src = None
    sqls.append("UPDATE %s SET image_date='%s',image='%s' WHERE cn='%s'" % (
        station_table, today, src, station))
    if len(sqls) == 10:
        mysql.execute(*sqls)
        sqls = []
    lock.release()


if __name__ == '__main__':
    sqls = []
    # get_station()
    # get_location()
    # get_location_thread('昭通南')
    # get_img()
    get_img_thread('广元')
