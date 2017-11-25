import time, redis, os
import ast, json, requests, random
from celery import Celery
################# Constants ##################
LIST_MODEM = 15


REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR','localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT_6379_TCP_PORT',6379))
redis_url = "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT)

REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR','localhost')
conn = redis.Redis(REDIS_HOST)

CELERY_BROKER_URL=redis_url
CELERY_RESULT_BACKEND=redis_url
RP_MESSAGES= os.getenv('RP_MESSAGES', "")


celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


@celery.task(name='tasks.request_to_rp')
def get_last_msgs():
    # Request all messages:
    resp = requests.get(url=RP_MESSAGES)
    data = json.loads(resp.text)

    for item in data['results']:
        contact_cel = item['contact']
        message = item['message']

        #### Redis ask to assign work
        if conn.get(contact_cel) is None:
            channel_queue = random.randint(0,LIST_MODEM-1)
            conn.set(contact_cel, idx_channel)
        else:
            channel_queue = conn.get(contact_cel)

        message = {"contact":contact_cel, "message": message}
        message_dump = json.dumps(message)
        conn.rpush(channel_queue, message_dump)
