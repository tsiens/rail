import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.config import *


def get_station():
    old_stations = pd.read_sql_table(station_table, con).drop('en', axis=1)
    new_stations = pd.DataFrame(
        re.findall('@\w+\|([\u4e00-\u9fa5]+)\|(\w+)', requests.get(get_station_url, verify=False).text),
        columns=['cn', 'en'])
    stations = old_stations.merge(new_stations, on=['cn'], how='outer')
    reset_db(stations, station_table, ['date', 'en', 'cn'])


def get_location():
    global stations
    stations = pd.read_sql(
        "SELECT * FROM (SELECT * From %s)t1 RIGHT JOIN (SELECT DISTINCT station FROM %s)t2 ON t1.cn=t2.station" % (
            station_table, timetable_table), con)
    stations['cn'] = stations['station']
    del stations['station']
    stations.index = stations['cn']
    stations_nodata = stations[
        (stations[['province']].isnull().any(axis=1))
        &
        (
                (stations[['date']].isnull().any(axis=1))
                |
                (pd.to_datetime(stations['date']) < datetime.now() - timedelta(days=10))
        )
        ]['cn'].tolist()
    rs = threadpool.makeRequests(get_location_thread, stations_nodata[:100])
    [pool.putRequest(r) for r in rs]
    pool.wait()
    reset_db(stations, station_table, ['date', 'en', 'cn'])


def get_location_thread(station):
    def get_amap(location):
        get = getjson(amap_url % (station, location, amap_sak))
        for row in get.get('pois', []):
            if station + '站' in row['name']:
                location = row['location'].split(',')
                province = row.get('pname', None)
                city = row.get('cityname', None)
                county = row.get('adname', None)
                get = getjson(amap_to_baidu % (location[0], location[1], baidu_sak))
                x = round(get['result'][0]['x'], 6)
                y = round(get['result'][0]['y'], 6)
                return [x, y, province, city, county]
        return [125, 30, None, None, None]

    def get_railmap():
        get = getjson(railmap_url % station)
        if get and get.get('station_position', None):
            y, x = get.get('station_position').get('ll', [30, 125])
            get = getjson(amap_geocode_url % (amap_sak, x, y))
            info = get.get('regeocode', {}).get('addressComponent', {})
            province = info.get('province', None)
            city = info.get('city', None)
            district = info.get('district', None)
            if not city:
                city = province
            get = getjson(amap_to_baidu % (x, y, baidu_sak))
            x = round(get['result'][0]['x'], 6)
            y = round(get['result'][0]['y'], 6)
            return [x, y, province, city, district]
        else:
            return [125, 30, None, None, None]

    def get_baidu(location):
        get = getjson(baidu_url % (station, location if location else '北京', baidu_sak))
        for row in get.get('results', []):
            if station + '站' in row['name']:
                province = row.get('province', None)
                city = row.get('city', None)
                county = row.get('area', None)
                return [row['location']['lng'], row['location']['lat'], province, city, county]
        return [125, 30, None, None, None]

    station = station.replace(' ', '')
    x, y, province, city, county = get_amap('全国')
    if not county:
        x, y, province, city, county = get_railmap()
    if not county:
        try:
            code = getjson(geogv_url1 % station)['data'][0][0]
            location = getjson(geogv_url2 % code)['location'].split(' ')[1]
            x, y, province, city, county = get_amap(location)
            if not county:
                x, y, province, city, county = get_baidu(location)
        except:
            province, city, county = None, None, None
    if province:
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
        if province in provinces and city == province:
            county, city = city, province + '属'
        elif city in citys:
            county = city + '属'
        elif city in countys:
            city = province + '属'

    lock.acquire()
    if not county:
        sql = "select t2.line as line,t2.station as cn from (select line,`order` from %s where station='%s')t1 join (select * from %s)t2 on t1.line=t2.line where t1.order=t2.order-1" % (
            timetable_table, station, timetable_table)
        x, y = pd.read_sql(sql, con).merge(stations[['cn', 'x', 'y']], on='cn').mean()[['x', 'y']].round(6).tolist()
        log('预测 %s 站 [%s,%s] %s %s %s' % (station, x, y, province, city, county))
    else:
        log('查询 %s 站 [%s,%s] %s %s %s' % (station, x, y, province, city, county))
    stations.loc[station, ['x', 'y', 'province', 'city', 'county', 'date']] = x, y, province, city, county, today
    lock.release()


def get_img():
    global stations
    stations = pd.read_sql_table(station_table, con)
    stations.index = stations['cn']
    stations_noimg = stations[
        (
                (
                    stations[['image']].isnull().any(axis=1)
                )
                &
                (
                        (stations[['image_date']].isnull().any(axis=1))
                        |
                        (pd.to_datetime(stations['image_date']) < datetime.now() - timedelta(days=10))
                )
        )
        |
        (pd.to_datetime(stations['image_date']) < datetime.now() - timedelta(days=6 * 30))
        ]['cn'].tolist()
    rs = threadpool.makeRequests(get_img_thread, stations_noimg[:100])
    [pool.putRequest(r) for r in rs]
    pool.wait()
    reset_db(stations, station_table, ['date', 'en', 'cn'])


def get_img_thread(station):
    src = pq(requests.get(baike_url % station, headers=headers).text)('#J-summary-img').attr('data-src')
    if src:
        qiniuyun.fetch(re.findall(r'src=(.+)', src)[0], 'station_img/%s.jpg' % station)
        log('图片 %s 站' % station)
    else:
        src = None
    lock.acquire()
    stations.loc[station, ['image', 'image_date']] = src, today
    lock.release()


if __name__ == '__main__':
    # get_station()
    # get_location()
    # get_location_thread('秋草地')
    get_img()
