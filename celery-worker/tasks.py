import os
import time, redis
from celery import Celery
import ast, json, requests, random
from gammu_load import *


env=os.environ
REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR','localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT_6379_TCP_PORT',6379))
redis_url = "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT)

REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR','localhost')
conn = redis.Redis(REDIS_HOST)

CELERY_BROKER_URL=redis_url
CELERY_RESULT_BACKEND=redis_url
RP_URL= os.getenv('RP_URL', "")
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
        task = celery.send_task('mytasks.send_sms', args=[item['contact'], item['message']],kwargs={})



@celery.task(name='tasks.send_kannel_response')
def send_client_responses():
    ####### Proxy to check all channels responses
    for i in range(len(list_modem)):
        task = celery.send_task('mytasks.send_to_rp', args = [i],kwargs={})


@celery.task(name='mytasks.send_sms')
def send_response(contact_cel, answer):
    try:
        payload = {"Text": answer_constant,"SMSC": {"Location":1},"Number": contact_cel}
        #### Check if have a channel of contact
        if conn.get(contact_cel) is None:
            idx_channel = random.randint(0,len(list_modem)-1)
            conn.set(contact_cel, idx_channel)
        else:
            idx_channel = conn.get(contact_cel)
        # Send SMS if all is OK
        list_modem[idx_channel].SendSMS(payload)
        print ('Success, SMS was Sent')
        return (True,payload)
    except gammu.GSMError:
        # Show error if message not sent
        print ('Error, SMS not Sent')
        return (False, payload)


@celery.task(name ='mytasks.send_to_rp')
def send_to_rp(channel_idx):

    #Obtain responses from gammu channel and send to kannel
    # Check if channel_idx exist
    if (channel_idx < len(list_modem)):
        sm = list_modem[channel_idx]
        status = list_modem[channel_idx].GetSMSStatus()
        remain = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']
        start = True
        sms = None
        while remain > 0:
            if start:
                sms = sm.GetNextSMS(Start = True, Folder = 0)
                start = False
            else:
                sms = sm.GetNextSMS(Location = sms[0]['Location'], Folder = 0)
            remain = remain - len(sms)
        if sms:
            for m in sms:
                payload={"backend":"Telcel","sender":m['Number'], "message":   m['Text'],"ts":"1", "id":"758af0a175f8a86"}
                r = request.get(RP_URL, params = payload)

    return (channel_idx, len(sms) if sms else 0)
