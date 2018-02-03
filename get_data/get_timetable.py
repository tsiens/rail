import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.config import *

def get_timetable_thread(info):
    line, start, arrive, code, start_en, arrive_en = info.split('-|-')
    get = getjson(get_timetable_url % (code, start_en, arrive_en, tomorrow))
    data = []
    order, day, runtime = 1, 1, 0
    if not get:
        return None
    for row in get.get('data', {}).get('data', []):
        station, arrivetime, leavetime = row['station_name'], row['arrive_time'], row['start_time']
        if arrivetime == '----': arrivetime = leavetime
        if leavetime == '----': leavetime = arrivetime
        arrivetime = datetime.strptime('1970-01-01' + arrivetime, "%Y-%m-%d%H:%M") + timedelta(days=day)
        if order == 1:
            lasttime = arrivetime
        if arrivetime < lasttime:
            arrivetime += timedelta(days=1)
            day += 1
        arrivedate = day
        leavetime = datetime.strptime('1970-01-01' + leavetime, "%Y-%m-%d%H:%M") + timedelta(days=day)
        if leavetime < arrivetime:
            leavetime += timedelta(days=1)
            day += 1
        leavedate = day
        staytime = int((leavetime - arrivetime).total_seconds() / 60)
        runtime += int((leavetime - lasttime).total_seconds() / 60)
        lasttime = leavetime
        data.append([line, code, order, station, arrivedate, arrivetime.time(), leavedate, leavetime.time(), staytime])
        order += 1
    global sqls
    lock.acquire()
    if len(data) > 1:
        log('检索 %s 次  %s - %s  %s%%' % (line, start, arrive,
                                        int(lines_list.index(info) / len(lines_list) * 100)))
        data[0][-1] = -1
        data[-1][-1] = -2
        sqls += [("INSERT INTO %s VALUE (null,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s)" % timetable_table, data),
                 "UPDATE %s SET runtime='%s',date='%s' WHERE code='%s'" % (line_table, runtime, today, code)]
    else:
        log('检索 %s 次  无效  %s - %s  %s%%' % (line, start, arrive, int(lines_list.index(info) / len(lines_list) * 100)))
        sqls.append("UPDATE %s SET date='%s' WHERE code='%s'" % (line_table, today, code))
    if len(sqls) == 10:
        mysql.execute(*sqls)
        sqls = []
    lock.release()

def get_timetable(old=[]):
    global stations_cn, stations_en, lines, lines_list, sqls
    sqls = []
    stations_cn, stations_en, lines = stations_lines()
    lines_list = mysql.execute(
        "SELECT line,start,arrive,code,start_en,arrive_en FROM %s WHERE date IS NULL" % line_table)
    lines_list = sorted(['-|-'.join(lines) for lines in lines_list])
    if lines_list != old:
        rs = threadpool.makeRequests(get_timetable_thread, lines_list)
        [pool.putRequest(r) for r in rs]
        pool.wait()
        mysql.execute(*sqls)
        get_timetable(lines_list)
if __name__ == '__main__':
    get_timetable()

