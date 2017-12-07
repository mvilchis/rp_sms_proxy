from threading import Thread
import os, redis, requests,time,json, random
##########      Priority queues   ############
from rpq.RpqQueue import RpqQueue

from gammu_load import *


REDIS_HOST = 'localhost'
LIST_MODEM = 15
LIST_QUEUE = [RpqQueue(redis.StrictRedis(host=REDIS_HOST, port=6379, db=idx), 'simple_queue') for idx in range (1, 1+LIST_MODEM)]

conn = redis.Redis(REDIS_HOST)
RP_URL= os.getenv('RP_URL', "")

def sm_callback(sm, type, data):
    if not data.has_key('Number'):
        data = sm.GetSMS(data['Folder'], data['Location'])[0]
        payload={"backend":"Telcel",
                "sender":data['Number'],
                "message":data["Text"],
                "ts":"1",
                "id":"758af0a175f8a86"}
        r = requests.get(RP_URL, params = payload)
    else:
        print data

def send_sms(sm_item, idx):
    while True:
        ######### Check if  have to send sms
        if LIST_QUEUE[idx].count() > 0:
            for i in range(LIST_QUEUE[idx].count()):
                data = json.loads(LIST_QUEUE[idx].popOne())
                payload = {"Text": data["message"],"SMSC": {"Location":1},"Number": data["contact"]}
                try:
                    sm_item.SendSMS(payload)
                    conn.incr(str(idx)+"_sent_sms")
                except gammu.GSMError:
                    # Show error if message not sent
                    print ('Error, SMS not SENT en canal %d' %idx)
                    print (payload)
                    if "counter" in data.keys():
                        data["counter"] = 1 + data["counter"]
                    else:
                        data["counter"] = 0
                    if data["counter"] <= 4: #Only try to resend three times 
                        message_dump = json.dumps(data)
                        try_on_queue = random.randint(0,LIST_MODEM-1)
                        LIST_QUEUE[try_on_queue].push(message_dump,100)
                    conn.incr(str(idx)+"_failed_sms")
        else:
            try:
                status = sm_item.GetBatteryCharge()
            except:
                pass
            time.sleep(1)


def create_thread(sm_item,idx):
    sm_item.SetIncomingCallback(sm_callback)
    try:
        sm_item.SetIncomingSMS()
    except gammu.ERR_NOTSUPPORTED:
        print 'Your phone does not support incoming SMS notifications!'
    # We need to keep communication with phone to get notifications
    thread = Thread(target = send_sms, args = (sm_item,idx ))
    thread.start()
    return

def test():
    # 14
    list_modem=[]
    sm_item = load_gsm(list_modem,27)
    sm_item = list_modem[0]
    idx = 14
    sm_item.SetIncomingCallback(sm_callback)

    try:
        sm_item.SetIncomingSMS()
    except gammu.ERR_NOTSUPPORTED:
        print 'Your phone does not support incoming SMS notifications!'

    send_sms(sm_item, idx)

def main():
   load_all()
   for i in range(len(list_modem)):
        create_thread(list_modem[i], i)

main()
