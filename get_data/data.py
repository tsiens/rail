from get_station import *
from get_line import *
from get_timetable import *


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
