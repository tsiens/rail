from config import *
import re
get_station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
amap_url = 'http://restapi.amap.com/v3/place/text?&types=火车站&keywords=%s站&city=%s&output=json&offset=20&page=1&key=%s'
amap_to_baidu = 'http://api.map.baidu.com/geoconv/v1/?coords=%s,%s&from=3&to=5&ak=%s'
geogv_url1 = 'http://cnrail.geogv.org/api/v1/match_feature/%s?locale=zhcn&query-over'
geogv_url2 = 'http://cnrail.geogv.org/api/v1/station/%s?locale=zhcn&query-over'
baike_url = 'https://wapbaike.baidu.com/item/%s站'
image_url = 'https://m.baidu.com/sf/vsearch?pd=image_content&atn=page&word=%s火车站'
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 7.0; zh-CN; SM-G9300 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.89 UCBrowser/11.5.6.946 Mobile Safari/537.36'}

stations = mysql_db.execute("SELECT cn,en FROM %s" % station_table)
stations_cn = dict(zip([station[0] for station in stations], [station[1] for station in stations])) if stations != [
    ()] else {}
stations_en = dict(zip([station[1] for station in stations], [station[0] for station in stations])) if stations != [
    ()] else {}


def get_station():
    get = re.findall('@[^@]+', requests.get(get_station_url, verify=False).text)
    data = []
    for station in get:
        cn, en = station.split('|')[1:3]
        if cn not in stations_cn:
            data.append((cn, en, 125, 30, None, None, None, None, '1970-01-01'))
            stations_cn[cn] = en
            stations_cn[en] = cn
            print('%s 插入 %s 站' % (datetime.now().strftime('%H:%M:%S'), cn))
    mysql_db.execute(("INSERT INTO %s VALUE (null,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s)" % station_table, data))


def get_location():
    stations = mysql_db.execute(
        "SELECT cn FROM %s WHERE x=125 and y=30 and cn in (SELECT station FROM %s) and date<'%s'" % (
            station_table, timetable_table, today))
    sqls = []
    for station in stations:
        station = station[0]
        data = get_station_location(station)
        print('%s 查询 %s 站 [%s,%s] %s %s %s' % (datetime.now().strftime('%H:%M:%S'), *data))
        sqls.append("UPDATE %s SET x='%s',y='%s',province='%s',city='%s',county='%s',date='%s' WHERE cn='%s'" % (
            station_table, *data[1:], today, station))
        if len(sqls) == 10:
            mysql_db.execute(*sqls)
            sqls = []
    if len(sqls) > 0:
        mysql_db.execute(*sqls)


def get_station_location(station):
    def get_amap(city):
        get = getjson(amap_url % (station, city, amap_sak))
        for data in get.get('pois', []):
            if station + '站' in data['name']:
                location = data['location'].split(',')
                pname = data.get('pname', '')
                cityname = data.get('cityname', '')
                adname = data.get('adname', '')
                get = getjson(amap_to_baidu % (location[0], location[1], baidu_sak))
                x = round(get['result'][0]['x'], 6)
                y = round(get['result'][0]['y'], 6)
                return [station, x, y, pname, cityname, adname]
        for data in get.get('suggestion', {}).get('cities', []):
            location = get_amap(data['name'])
            if location:
                return location
        return None

    station = station.replace(' ', '')
    location = get_amap('全国')
    if location:
        return location
    try:
        code = getjson(geogv_url1 % station)['data'][0][0]
        city = getjson(geogv_url2 % code)['location'].split(' ')[-1]
        location = get_amap(city)
        if location:
            return location
    except:
        pass
    return [station, 125, 30, None, None, None]


def get_img():
    stations = mysql_db.execute(
        "SELECT cn FROM %s WHERE cn in (SELECT station FROM %s) and (image_url is null or image_url='None' or date<'%s')" % (
            station_table, timetable_table, today - timedelta(days=100)))
    sqls = []
    for station in stations:
        station = station[0]
        src = get_station_img(station)
        sqls.append("UPDATE %s SET image_url='%s',date='%s' WHERE cn='%s'" % (
            station_table, src, today, station))
        print('%s 图片 %s 站 %s' % (datetime.now().strftime('%H:%M:%S'), station, src))
        if len(sqls) == 10:
            mysql_db.execute(*sqls)
            sqls = []
    if len(sqls) > 0:
        mysql_db.execute(*sqls)


def get_station_img(station):
    try:
        src = pq(requests.get(baike_url % station, headers=headers).text)('#J-summary-img').attr('data-src')
        src = re.findall(r'src=(.+)', src)[0]
    except:
        src = None
    if src:
        return src
    try:
        html = requests.get(image_url % station, headers=headers).text
        src = re.findall(r'"thumburl":"(.+?\.jpg)"', html)[0].replace('\\', '')
    except:
        src = None
    return src

if __name__ == '__main__':
    # get_station()
    # get_location()
    # print(get_station_location('绥阳'))
    get_img()
