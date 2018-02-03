import logging
import os
import sys
import threading
from datetime import *

import requests
import threadpool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.mysql import Mysql
from get_data.qiniuyun import Qiniuyun
from key import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler(os.path.dirname(os.path.abspath(__file__)) + '/data.log', mode='a+')  # 文件
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()  # 控制台
ch.setLevel(logging.ERROR)
fh.setFormatter(logging.Formatter('||%(levelname)s-|-%(asctime)s-|-%(message)s', datefmt='%H:%M:%S'))
ch.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S'))
logger.addHandler(fh)
logger.addHandler(ch)
log = logging.error

basename = 'rail'
tables = {}
station_table, line_table, timetable_table = 'web_station', 'web_line', 'web_timetable'
mysql = Mysql(mysql_host, mysql_user, mysql_pwd, basename, tables)
bucket_name = 'rail'
qiniuyun = Qiniuyun(qiniu_ak, qiniu_sk, bucket_name)

pool = threadpool.ThreadPool(10)
lock = threading.Lock()

today = datetime.now().date()
tomorrow = (datetime.now() + timedelta(days=1)).date()

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 7.0; zh-CN; SM-G9300 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/40.0.2214.89 UCBrowser/11.5.6.946 Mobile Safari/537.36'}

get_station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
get_lines_url = 'https://kyfw.12306.cn/otn/resources/js/query/train_list.js'
get_timetable_url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=%s&from_station_telecode=%s&to_station_telecode=%s&depart_date=%s'
get_ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT'

amap_url = 'http://restapi.amap.com/v3/place/text?&types=火车站&keywords=%s站&city=%s&output=json&offset=20&page=1&key=%s'
amap_to_baidu = 'http://api.map.baidu.com/geoconv/v1/?coords=%s,%s&from=3&to=5&ak=%s'
baidu_url = 'http://api.map.baidu.com/place/v2/search?query=%s站&tag=火车站&region=%s&output=json&ak=%s'
geogv_url1 = 'http://cnrail.geogv.org/api/v1/match_feature/%s?locale=zhcn&query-over'
geogv_url2 = 'http://cnrail.geogv.org/api/v1/station/%s?locale=zhcn&query-over'
wiki_url = 'https://zh.wikipedia.org'
baike_url = 'https://wapbaike.baidu.com/item/%s站'


def stations_lines():
    stations, lines = mysql.execute("SELECT cn,en FROM %s" % station_table, "SELECT code,date FROM %s" % line_table)
    stations_cn = dict(zip([station[0] for station in stations], [station[1] for station in stations])) if stations != [
        ()] else {}
    stations_en = dict(zip([station[1] for station in stations], [station[0] for station in stations])) if stations != [
        ()] else {}
    lines = dict(zip([line[0] for line in lines], [line[1] for line in lines])) if lines != [()] else []
    for k, v in lines.items():
        if not v:
            lines[k] = datetime(1970, 1, 1).date()
    return stations_cn, stations_en, lines

def getjson(url, n=0):
    try:
        return requests.get(url, verify=False).json()
    except:
        if n < 100:
            return getjson(url, n + 1)
        return False
