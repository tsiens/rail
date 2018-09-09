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
        data.append(
            [line, code, str(order), station, arrivedate, arrivetime.time(), leavedate, leavetime.time(), staytime])
        order += 1
    if len(data) > 1:
        data[0][-1] = -1
        data[-1][-1] = -2
        con.execute("INSERT INTO %s VALUE (null,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s)" % timetable_table, data)
        lines.loc[code, 'runtime'] = runtime
        log('检索 %s 次  %s - %s' % (line, start, arrive))
    else:
        log('检索 %s 次  无效  %s - %s' % (line, start, arrive))


def get_timetable(old=[]):
    global lines
    lines = pd.read_sql_table(line_table, con)
    lines.index = lines['code']
    lines_nodata = pd.read_sql(
        "SELECT line,start,arrive,code,start_en, arrive_en FROM %s where runtime IS NULL" % line_table, con).apply(
        lambda x: '-|-'.join(x), axis=1).values.tolist()

    if lines_nodata != old:
        rs = threadpool.makeRequests(get_timetable_thread, lines_nodata)
        [pool.putRequest(r) for r in rs]
        pool.wait()
        reset_db(lines.dropna(), line_table, sort_key='line')
        return get_timetable(lines_nodata)



if __name__ == '__main__':
    get_timetable()
