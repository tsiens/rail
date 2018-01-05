import threading, threadpool
import requests, re, pymysql
from prettytable import PrettyTable  # 表格输出
from datetime import *
from get_data.mysql import *
from key import *

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
