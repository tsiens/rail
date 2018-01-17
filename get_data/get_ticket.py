import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.config import *

def get_ticket(start, arrive, date, ticker=True):
    global stations_cn, stations_en, lines
    stations_cn, stations_en, lines = stations_lines()
    if len(date) < 3:
        year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        date = str(datetime(year, month + 1 if int(date) < day else month, int(date)).date())
    print(date)
    get = getjson(get_ticket_url % (date, stations_cn[start], stations_cn[arrive]))
    if get.get('status', None) == False:
        query = get['c_url'].split('/')[1]
        get = getjson(re.sub('query.', query, get_ticket_url % (date, stations_cn[start], stations_cn[arrive])))
    if not get:
        return []
    data = []
    for line in get.get('data', {}).get('result', []):
        line = line.split('|')
        code, name, sf, zd, cf, dd = line[2:8]
        cftime, ddtime, ls = line[8:11]
        cf = stations_en[cf]
        dd = stations_en[dd]
        if ticker:
            sw, yd, ed, gr, rw, dw, yw, rz, yz, wz = line[32], line[31], line[30], line[21], line[23], line[33], line[
                28], line[24], line[29], line[26]
            data.append([name, cf, dd, cftime, ddtime, ls, sw, yd, ed, gr, rw, dw, yw, rz, yz, wz])
        else:
            data.append((name, code, sf, zd))
    return data


if __name__ == '__main__':
    start = '杭州'
    arrive = '缙云'
    print('%s号: %s - %s ' % (6, start, arrive))
    table = PrettyTable(
        ['车次', '出发', '到达', '发时', '到时', '历时', '商务座', '一等座', '二等座', '高级软卧', '软卧', '动卧', '硬卧', '软座', '硬座', '无座'])
    for i in get_ticket(start, arrive, '6'):
        table.add_row(i)
    print(table)
