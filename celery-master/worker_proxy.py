import os, requests, json
from celery import Celery
from celery.decorators import periodic_task
from datetime import timedelta
from celery.schedules import crontab
import inspect, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants  import *



celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

celery.conf.CELERYBEAT_SCHEDULE = {
    'check-every-30-seconds': {
        'task': 'tasks.request_to_rp',
        'schedule': timedelta(seconds=10)
    },
    'check-every-120-seconds': {
        'task': 'tasks.request_to_dashboard',
        'schedule': timedelta(seconds=120)
    },
    'check-every-5-mins': {
        'task': 'tasks.request_ping_dashboard',
        'schedule': timedelta(minutes=5)
    },
    'send_mail_report_1': {
        'task': 'tasks.report_channels',
        'schedule': crontab(hour=0, minute=30)
    },
    'send_mail_report_2': {
        'task': 'tasks.report_inclusion',
        'schedule': crontab(hour=0, minute=30)
    },
    'send_mail_report_2': {
        'task': 'tasks.report_channels',
        'schedule': crontab(hour=15, minute=30)
    },
    'send_mail_report_3': {
        'task': 'tasks.report_channels',
        'schedule': crontab(hour=17, minute=30)
    },
    'ping_sms': {
        'task': 'tasks.send_ping',
        'schedule': crontab(hour=17, minute=30)
    },
}
