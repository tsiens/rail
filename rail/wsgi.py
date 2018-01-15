"""
WSGI config for rail project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rail.settings")

application = get_wsgi_application()

import platform

if platform.system() == 'Linux':
    # 定时器
    import uwsgi
    from data import *

    for job_id, job in enumerate(jobs):
        uwsgi.register_signal(job_id, "", job['name'])
        if len(job['time']) == 1:
            uwsgi.add_timer(job_id, job['time'][0])
        else:
            uwsgi.add_cron(job_id, job['time'][0], job['time'][1], job['time'][2], job['time'][3], job['time'][4])
