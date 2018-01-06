from get_data.get_station import *
from get_data.get_line import *
from get_data.get_timetable import *


def cron(signum):
    get()


jobs = [{'name': cron, 'time': [1, 0, -1, -1, -1]},  # 分,时，日，月，周几
        # {'name': cron,'time': [5]},#每隔2秒
        ]


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
