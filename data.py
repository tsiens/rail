from get_data.get_station import *
from get_data.get_line import *
from get_data.get_timetable import *


def clock_get(signum):
    get()

def clock_log(signum):
    delete_log()


jobs = [{'name': clock_get, 'time': [1, 0, -1, -1, -1]},  # 分,时，日，月，周几
        {'name': clock_log, 'time': [1, 0, -1, -1, 1]},  # 每周一清空日志
        # {'name': clock_get,'time': [60]},#每隔60秒
        ]


def delete_log():
    for path in ['/home/service/rail/access.log', '/home/service/rail/error.log',
                 '/home/service/rail/uwsgi.log', '/home/rail/get_data/data.log']:
        with open(path, 'w') as f:
            f.write('')

def get():
    try:
        get_station()
        get_line()
        get_timetable()
        get_location()
        get_img()
    except:
        logger.error(traceback.format_exc())
    log('数据爬取完成')


if __name__ == '__main__':
    get()
