import sys, os

sys.path += ['get_data', '/home/rail/get_data']
from get_station import *
from get_line import *
from get_timetable import *


def main():
    get_station()
    get_line()
    get_timetable()
    get_location()
    get_img()


if __name__ == '__main__':
    main()
