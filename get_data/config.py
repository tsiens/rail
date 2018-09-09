import os
import sys
import re
import logging
import threadpool
import threading
import requests
from datetime import *
from pyquery import PyQuery as pq
import pandas as pd
from sqlalchemy import create_engine
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.qiniuyun import Qiniuyun
from key import *
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler(os.path.dirname(os.path.abspath(__file__)) + '/data.log', mode='a+')  # 文件
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()  # 控制台
ch.setLevel(logging.ERROR)
fh.setFormatter(logging.Formatter('||%(levelname)s-|-%(asctime)s-|-%(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
ch.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(fh)
logger.addHandler(ch)
log = logging.error

rail_db = {
    'host': mysql_host,
    'database': 'rail',
    'username': mysql_user,
    'password': mysql_pwd}
station_table, line_table, timetable_table = 'web_station', 'web_line', 'web_timetable'
con = create_engine('mysql+pymysql://%(username)s:%(password)s@%(host)s/%(database)s?charset=utf8' % rail_db)

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

amap_url = 'http://restapi.amap.com/v3/place/text?&types=火车站&keywords=%s站&city=%s&output=json&offset=20&page=1&key=%s'
amap_to_baidu = 'http://api.map.baidu.com/geoconv/v1/?coords=%s,%s&from=3&to=5&ak=%s'
baidu_url = 'http://api.map.baidu.com/place/v2/search?query=%s站&tag=火车站&region=%s&output=json&ak=%s'
geogv_url1 = 'http://cnrail.geogv.org/api/v1/match_feature/%s?locale=zhcn&query-over'
geogv_url2 = 'http://cnrail.geogv.org/api/v1/station/%s?locale=zhcn&query-over'
railmap_url = 'http://www.railmap.cn/api/stationpos/%s/'
amap_geocode_url = 'http://restapi.amap.com/v3/geocode/regeo?key=%s&location=%s,%s'
wiki_url = 'https://zh.wikipedia.org'
baike_url = 'https://wapbaike.baidu.com/item/%s站'


def reset_db(data, table, sort_key=None):
    data.index = pd.RangeIndex(1, len(data) + 1)
    if sort_key:
        data = data.sort_values(sort_key, ascending=False)
    data['id'] = pd.RangeIndex(1, len(data) + 1)
    backup = pd.read_sql_table(table, con)
    try:
        con.execute('truncate %s' % table)
        data.to_sql(table, con, if_exists='append', index=False, chunksize=1000)
    except:
        backup.to_sql(table, con, if_exists='append', index=False, chunksize=1000)


def getjson(url, n=0):
    try:
        return requests.get(url, verify=False).json()
    except:
        if n < 10:
            return getjson(url, n + 1)
        return False
