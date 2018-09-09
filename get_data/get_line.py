import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.config import *


def get_line():
    html = requests.get(get_lines_url, verify=False).text
    get = re.findall('"%s":.+?}]}' % tomorrow, html)
    if len(get) == 0:
        return None
    stations = pd.read_sql('SELECT cn,en FROM %s' % station_table, con).set_index('cn')
    old_lines = pd.read_sql_table(line_table, con)
    new_lines = pd.DataFrame(
        re.findall('{"station_train_code":"([^\)]+)\(([^-]+)-([^\)]+)\)","train_no":"([^\"]+)"}', get[0]),
        columns=['line', 'start', 'arrive', 'code'])
    new_lines_concat = pd.DataFrame(new_lines.groupby(by='code').apply(lambda x: '/'.join(x['line'])), columns=['line'])
    new_lines_uniq = new_lines.drop('line', axis=1).drop_duplicates('code')
    new_lines_1 = new_lines_concat.merge(new_lines_uniq, left_index=True, right_on='code')
    new_lines_2 = new_lines_1.merge(stations.rename(columns={'en': 'start_en'}), left_on='start',
                                    right_index=True).merge(
        stations.rename(columns={'en': 'arrive_en'}), left_on='arrive', right_index=True).dropna(
        subset=['start_en', 'arrive_en'])
    lines = pd.concat([old_lines, new_lines_2], sort=True).drop_duplicates('code')
    lines['date'] = today
    delete_line = pd.concat([lines, lines, old_lines], sort=True).drop_duplicates('code', keep=False)['code'].tolist()
    if len(delete_line) > 0:
        log('删除 时刻表 %d 次' % len(delete_line))
        con.execute("DELEDE FROM %s WHERE code in ('')" % (timetable_table, "','".join(delete_line)))
    reset_db(lines, line_table, sort_key='line')


if __name__ == '__main__':
    get_line()
