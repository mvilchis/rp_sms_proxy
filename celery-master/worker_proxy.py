import os, requests, json
from celery import Celery
from celery.decorators import periodic_task
from datetime import timedelta


env=os.environ
##############     Read environment variables     ##############
REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT_6379_TCP_PORT',6379))
redis = "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT)


#############     Configure celery beat          ###############
CELERY_BROKER_URL=redis
CELERY_RESULT_BACKEND=redis
CELERY_RESULT_SERIALIZER = 'json'
celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

celery.conf.CELERYBEAT_SCHEDULE = {
    'check-every-30-seconds': {
        'task': 'tasks.request_to_rp',
        'schedule': timedelta(seconds=30)
    },
    'send-client-response' :{
        'task' : 'tasks.send_kannel_response',
        'schedule': timedelta(seconds = 30)


    }
}
