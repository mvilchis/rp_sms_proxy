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
        'schedule': timedelta(seconds=10)
    },
    'send_mail_report_2': {
        'task': 'tasks.report_inclusion',
        'schedule': crontab(hour=0, minute=30)
    },
    'ping_sms': {
        'task': 'tasks.send_ping',
        'schedule': crontab(hour=17, minute=30)
    },
}
