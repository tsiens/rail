import os
import sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_data.get_station import *
from get_data.get_line import *
from get_data.get_timetable import *


def get():
    try:
        get_station()
        get_line()
        get_timetable()
        get_location()
        get_img()
        log('数据爬取完成')
    except:
        logger.error(traceback.format_exc())


if __name__ == '__main__':
    get()
