import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.get_ticket import *
from get_data.get_timetable import *

def get_city_line_thread(city):
    global codes
    start, arrive = city.split('-')
    if start in stations_cn and arrive in stations_cn:
        for line in get_ticket(start, arrive, today, ticker=False):
            if line[1] not in codes:
                lock.acquire()
                codes.append(line[1])
                lock.release()


def get_city(citys):
    citys_list = sorted([city for city in citys], key=lambda city: citys[city], reverse=True)
    rs = threadpool.makeRequests(get_city_line_thread, citys_list)
    [pool.putRequest(r) for r in rs]
    pool.wait()
    log('检索 城市 %s 对' % len(citys_list))


def get_line():
    global stations_cn, stations_en, lines, codes
    stations_cn, stations_en, lines = stations_lines()
    codes = []
    html = requests.get(get_lines_url, verify=False).text
    get = re.findall('"%s":.+?}]}' % today, html)
    if get == []:
        data = re.findall(r'([\u4e00-\u9fa5\s]+-[\u4e00-\u9fa5\s]+)', html)
        citys = {}
        for city in set(data):
            citys[city] = data.count(city)
        get_city(citys)
    else:
        codes = re.findall('{"station_train_code":"([^\)]+)\(([^-]+)-([^\)]+)\)","train_no":"([^\"]+)"}', get[0])
    codes.sort(key=lambda x: (x[0][0], int(x[0][1:]) if len(x[0]) > 1 else 0))
    insert_line, update_line = {}, []
    for line in codes:
        name, start, arrive, code = line
        if start not in stations_cn or arrive not in stations_cn:
            continue
        if code in lines:
            if lines[code] < today:
                update_line.append(code)
                lines[code] = today
            else:
                if name not in insert_line.get(code, [name])[0]:
                    insert_line[code][0] = insert_line[code][0] + '/' + name
        else:
            insert_line[code] = [name, code, start, stations_cn[start], arrive, stations_cn[arrive]]
            lines[code] = today
    mysql.execute(
        ("INSERT INTO %s VALUE (null,%%s,%%s,%%s,%%s,%%s,%%s,null,null)" % line_table,
         [line for line in insert_line.values()]),
        "UPDATE %s SET date='%s' WHERE code in ('%s')" % (line_table, today, "','".join(update_line)))
    log('插入 车次 %s ' % len(insert_line))
    log('更新 车次 %s ' % len(update_line))
    lines_delete = mysql.execute(
        "SELECT code FROM %s WHERE date<'%s'" % (line_table, today))
    if len(lines_delete) > 0:
        lines_delete = [line[0] for line in lines_delete]
        mysql.execute("DELETE FROM %s WHERE code in('%s')" % (timetable_table, "','".join(lines_delete)),
                      "DELETE FROM %s WHERE code in('%s')" % (line_table, "','".join(lines_delete)))
    log('删除 车次 %s' % (len(lines_delete)))


if __name__ == '__main__':
    get_line()
