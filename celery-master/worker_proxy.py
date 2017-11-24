import os, requests, json
from celery import Celery
from datetime import timedelta


env=os.environ
##############     Read environment variables     ##############
REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT_6379_TCP_PORT',6379))
redis = "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT)
RP_MESSAGES= os.getenv('RP_MESSAGES', "")


#############     Configure celery beat          ###############
CELERY_BROKER_URL=redis
CELERY_RESULT_BACKEND=redis
celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

CELERYBEAT_SCHEDULE = {
    'check-every-30-seconds': {
        'task': 'tasks.request_to_rp',
        'schedule': timedelta(seconds=30)
    },
    'send-client-response' :{
        'task' : 'tasks.send_kannel_response',
        'schedule': timedelta(seconds = 30)


    }
}

@celery.task(name='tasks.request_to_rp')
def get_last_msgs():
    # Request all messages:
    resp = requests.get(url=RP_MESSAGES)
    data = json.loads(resp.text)
    for item in data['results']:
        task = celery.send_task('mytasks.send_sms', args=[item['contact'], item['message']],kwargs={})



@celery.task(name='tasks.send_kannel_response')
def send_client_responses():
    ####### Proxy to check all channels responses
    for i in range(32):
        task = celery.send_task('mytasks.send_to_rp', args = [i],kwargs={})
