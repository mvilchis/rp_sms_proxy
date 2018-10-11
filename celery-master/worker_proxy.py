import inspect
import json
import os
import sys
from datetime import timedelta

import requests
from celery import Celery
from celery.decorators import periodic_task
from celery.schedules import crontab

##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants import *

celery = Celery(
    'tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery.conf.CELERYBEAT_SCHEDULE = {
    'check-every-30-seconds': {
        'task': 'tasks.request_to_rp',
        'schedule': timedelta(seconds=20)
    },
    'send_mail_report_2': {
        'task': 'tasks.report_inclusion',
        'schedule': crontab(hour=1, minute=30)
    },
    'ping_sms': {
        'task': 'tasks.send_ping',
        'schedule': crontab(hour=17, minute=30)
    },
    'make_call_4': {
        'task': 'tasks.make_call',
        'schedule': crontab(hour=17, minute=00)
        'args': (4)
    },
    'make_call_5': {
        'task': 'tasks.make_call',
        'schedule': crontab(hour=17, minute=15)
        'args': (5)
    },
    'make_call_6': {
        'task': 'tasks.make_call',
        'schedule': crontab(hour=17, minute=20)
        'args': (6)
    },
    'make_call_7': {
        'task': 'tasks.make_call',
        'schedule': crontab(hour=17, minute=25)
        'args': (7)
    },
    'make_call_12': {
        'task': 'tasks.make_call',
        'schedule': crontab(hour=17, minute=35)
        'args': (12)
    },
    'make_call_13': {
        'task': 'tasks.make_call',
        'schedule': crontab(hour=17, minute=40)
        'args': (13)
    },
    'make_call_14': {
        'task': 'tasks.make_call',
        'schedule': crontab(hour=17, minute=45)
        'args': (14)
    }

}
