from get_data.config import *

def get_station():
    stations_cn, stations_en = stations_lines()[:2]
    get = re.findall('@[^@]+', requests.get(get_station_url, verify=False).text)
    data = []
    for station in get:
        cn, en = station.split('|')[1:3]
        if cn not in stations_cn:
            data.append((cn, en, 125, 30, None, None, None, '1970-01-01', '1970-01-01'))
            stations_cn[cn], stations_cn[en] = en, cn
            log('%s 插入 %s 站' % (datetime.now().strftime('%H:%M:%S'), cn))
    mysql.execute(("INSERT INTO %s VALUE (null,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s)" % station_table, data))


def get_location():
    stations = mysql.execute(
        "SELECT cn FROM %s WHERE x=125 and y=30 and cn in (SELECT station FROM %s) and date<'%s'" % (
            station_table, timetable_table, today))
    sqls = []
    for station in stations:
        station = station[0]
        station, x, y, p, c, co = get_station_location(station)
        log('查询 %s 站 [%s,%s] %s %s %s' % (station, x, y, p, c, co))
        sqls.append("UPDATE %s SET x='%s',y='%s',province='%s',city='%s',county='%s',date='%s' WHERE cn='%s'" % (
            station_table, x, y, p, c, co, today, station))
        if len(sqls) == 10:
            mysql.execute(*sqls)
            sqls = []
    if len(sqls) > 0:
        mysql.execute(*sqls)


def get_station_location(station):
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
                return [station, x, y, province, city, county]
        return None

    def get_baidu(province, city, county):
        get = getjson(baidu_url % (station, city if city else '北京', baidu_sak))
        for row in get.get('results', []):
            if station + '站' in row['name']:
                return [station, row['location']['lng'], row['location']['lat'], province, city, county]
        return None
    station = station.replace(' ', '')
    location = get_amap('全国')
    if location:
        return location
    try:
        code = getjson(geogv_url1 % station)['data'][0][0]
        province, city, county = getjson(geogv_url2 % code)['location'].split(' ')
        if city in ['东莞市', '中山市', '三沙市', '儋州市', '嘉峪关市']:
            county = city
    except:
        province, city, county = None, None, None
    for location in [get_amap(city), get_baidu(province, city, county)]:
        if location:
            return location
    return [station, 125, 30, province, city, county]


def get_img():
    stations = mysql.execute(
        "SELECT cn FROM %s WHERE cn in (SELECT station FROM %s) and image_date<'%s'" % (
            station_table, timetable_table, today - timedelta(days=100)))
    sqls = []
    for station in stations[:100]:
        station = station[0]
        src = get_station_img(station)
        sqls.append("UPDATE %s SET image_date='%s' WHERE cn='%s'" % (
            station_table, today, station))
        qiniuyun.fetch(src, 'station_img/%s.jpg' % station)
        log('图片 %s 站' % station)
        if len(sqls) == 10:
            mysql.execute(*sqls)
            sqls = []
    if len(sqls) > 0:
        mysql.execute(*sqls)

def get_station_img(station):
    src = pq(requests.get(wiki_url % station, headers=headers).text)('[property="og:image"]')
    if src:
        src = src.attr('content').replace('1200px', '640px')
        if 'Missing' not in src and 'No_free_image' not in src:
            return src
    src = pq(requests.get(baike_url % station, headers=headers).text)('#J-summary-img').attr('data-src')
    if src:
        return re.findall(r'src=(.+)', src)[0]
    html = requests.get(image_url % station, headers=headers).text
    return re.findall(r'"thumburl":"(.+?\.jpg)"', html)[0].replace('\\', '')

if __name__ == '__main__':
    # get_station()
    # get_location()
    get_img()
    # print(get_station_location('德兴东'))
    # print(get_station_img('北京南'))
