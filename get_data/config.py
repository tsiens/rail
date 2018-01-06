import sys, traceback, threading, threadpool, requests
sys.path.append('.')
from pyquery import PyQuery as pq
from datetime import *
from get_data.mysql import Mysql
from key import *
import logging

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('data.log', mode='w')  # 文件
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()  # 控制台
ch.setLevel(logging.WARNING)
fh.setFormatter(logging.Formatter('|%(levelname)s: %(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
ch.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
logger.addHandler(fh)
logger.addHandler(ch)
log = logging.warning

basename = 'rail'
tables = {}
station_table, line_table, timetable_table = 'web_station', 'web_line', 'web_timetable'

mysql_db = Mysql(mysql_host, mysql_user, mysql_pwd, basename, tables)

pool = threadpool.ThreadPool(10)
lock = threading.Lock()

today = datetime.now().date()
tomorrow = (datetime.now() + timedelta(days=1)).date()


def getjson(url, n=0):
    try:
        return requests.get(url, verify=False).json()
    except:
        if n < 100:
            return getjson(url, n + 1)
        return False
