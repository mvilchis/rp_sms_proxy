import os
import time
from celery import Celery
import ast, json, requests, random
"""from gammu_load import *"""


env=os.environ
REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR','redis')
REDIS_PORT = int(os.getenv('REDIS_PORT_6379_TCP_PORT',6379))
redis_url = "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT)


CELERY_BROKER_URL=redis_url
CELERY_RESULT_BACKEND=redis_url
RP_URL= os.getenv('RP_URL', "")



celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)




@celery.task(name='mytasks.send_sms')
def send_response(contact_cel, answer):
    payload={"backend":"Telcel","sender":"+525521817435", "message": "respuesta de automatica","ts":"1", "id":"758af0a175f8a86"}
    r = requests.get(RP_URL, params = payload)
    """try:
        payload = {"Text": answer_constant,"SMSC": {"Location":1},"Number": contact_cel}
        idx_random = random.randint(0,len(list_modem))
        # Send SMS if all is OK
        list_modem[idx_random].SendSMS(payload)
        print 'Success, SMS was Sent'
        return (True,payload)
    except gammu.GSMError:
        # Show error if message not sent
        print 'Error, SMS not Sent'
        return (False, payload)
    """


@celery.task(name ='mytasks.send_to_rp')
def send_to_rp(channel_idx):
    # Check if channel_idx exist
    """if (channel_idx < len(list_modem)):
        #Obtain responses from gammu channel and send to kannel
        payload={"backend":"Telcel","sender":"+52"+contact_cel, "message":   answer_constant,"ts":"1", "id":"758af0a175f8a86"}
        r = requests.get(RP_URL, params = payload)
    """
    return channel_idx
