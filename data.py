from get_data.get_station import *
from get_data.get_line import *
from get_data.get_timetable import *


def delete_log(signum):
    for path in ['/home/service/rail/access.log', '/home/service/rail/error.log',
                 '/home/service/rail/uwsgi.log', '/home/rail/get_data/data.log']:
        with open(path, 'w') as f:
            f.write('')


def get(signum):
    try:
        get_station()
        get_line()
        get_timetable()
        get_location()
        get_img()
    except:
        logger.error(traceback.format_exc())
    log('数据爬取完成')


jobs = [{'name': get, 'time': [0, 1, -1, -1, -1]},  # 分,时，日，月，周几
        {'name': delete_log, 'time': [0, 2, -1, -1, 1]},  # 每周一清空日志
        # {'name': get,'time': [60]},#每隔60秒
        ]

if __name__ == '__main__':
    get(None)
