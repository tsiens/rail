import os


def data(signum):
    os.system('python get_data/run.py')


def delete_log(signum):
    print('清空日志')
    for path in ['/home/service/rail/access.log', '/home/service/rail/error.log',
                 '/home/service/rail/uwsgi.log', '/home/rail/get_data/data.log']:
        with open(path, 'r+') as f:
            f.truncate()


jobs = [{'name': data, 'time': [1, 0, -1, -1, -1]},  # 分,时，日，月，周几
        {'name': delete_log, 'time': [0, 1, -1, -1, 1]},  # 每周日清空日志
        # {'name': get,'time': [60]},#每隔60秒
        ]
