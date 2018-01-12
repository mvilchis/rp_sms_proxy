from threading import Thread
import os, redis, requests,time,json, random
##########      Priority queues   ############
from rpq.RpqQueue import RpqQueue

from gammu_load import *


REDIS_HOST = 'localhost'
LIST_MODEM = 15
LIST_PROSPERA = 4
LIST_QUEUE = [RpqQueue(redis.StrictRedis(host=REDIS_HOST, port=6379, db=idx), 'simple_queue') for idx in range (1, 1+LIST_MODEM)]

conn = redis.Redis(REDIS_HOST)
RP_URL= os.getenv('RP_URL', "")
RP_URL_PROSPERA= os.getenv('RP_URL_PROSPERA', "")

def sm_callback(sm, type, data):
    if not data.has_key('Number'):
        data = sm.GetSMS(data['Folder'], data['Location'])[0]
        #Now delete sms
        sm.DeleteSMS(Folder = data['Folder'], Location = data['Location'])
    payload={"backend":"Telcel",
                "sender":data['Number'],
                "message":data["Text"],
                "ts":"1",
                "id":"758af0a175f8a86"}
    r = requests.get(RP_URL, params = payload)

def send_sms(sm_item, idx):
    start = True
    while True:
        ######### Check if  have to send sms
        if LIST_QUEUE[idx].count() > 0:
            for i in range(LIST_QUEUE[idx].count()):
                data = json.loads(LIST_QUEUE[idx].popOne())
                payload = {"Text": data["message"],"SMSC": {"Location":1},"Number": data["contact"]}
                try:
                    sm_item.SendSMS(payload)
                    conn.incr("_"+str(idx)+"_sent_sms")
                except gammu.GSMError:
                    # Show error if message not sent
                    if "counter" in data.keys():
                        data["counter"] = 1 + data["counter"]
                        try_on_queue = random.randint(0,LIST_MODEM-1)
                    else:
                        data["counter"] = 0
                        try_on_queue = idx
                    if data["counter"] <= 4: #Only try to resend three times
                        message_dump = json.dumps(data)
                        LIST_QUEUE[try_on_queue].push(message_dump,100)
                    else:
                        conn.incr("_"+str(idx)+"_not_sent_sms")
                        print ('Error, SMS not SENT en canal %d' %idx)
                        print (data)

                    conn.incr("_"+str(idx)+"_failed_sms")
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


###############         Prospera  Part       #########################

def send_sms_prospera(sm_item, idx):
    start = True

    while True:
        ######### Check if  have to send sms
        if conn.llen(idx) > 0:
            for i in range(conn.llen(idx)):
                data = json.loads(conn.lpop(idx))
                payload = {"Text": data["message"],"SMSC": {"Location":1},"Number": data["contact"]}
                try:
                    sm_item.SendSMS(payload)
                    conn.incr("_"+str(idx)+"_sent_sms_prospera")
                except gammu.GSMError:
                    # Show error if message not sent
                    if "counter" in data.keys():
                        data["counter"] = 1 + data["counter"]
                        try_on_queue = random.randint(0,LIST_PROSPERA-1)
                    else:
                        
                        data["counter"] = 0
                        data["first_attempt"] = idx
                        try_on_queue = idx
                    if data["counter"] <= 4: #Only try to resend three times
                        message_dump = json.dumps(data)
                        conn.rpush(try_on_queue,message_dump)
                    else:
                        conn.incr("_"+str(idx)+"_not_sent_sms_prospera")
                        print ('Error, Prospera SMS not SENT en canal %d' %idx)
                        print (data)

                    conn.incr("_"+str(idx)+"_failed_sms_prospera")
        else:
            try:
                status = sm_item.GetBatteryCharge()
            except:
                pass
            time.sleep(1)

def sm_callback_prospera(sm, type, data):
    if not data.has_key('Number'):
        data = sm.GetSMS(data['Folder'], data['Location'])[0]
        payload={"backend":"Telcel",
                "sender":data['Number'],
                "message":data["Text"],
                "ts":"1",
                "id":"758af0a175f8a86"}
        r = requests.get(RP_URL_PROSPERA, params = payload)
    else:
        print data

def create_prospera_thread(sm_item,idx):
    sm_item.SetIncomingCallback(sm_callback_prospera)
    try:
        sm_item.SetIncomingSMS()
    except gammu.ERR_NOTSUPPORTED:
        print 'Your phone does not support incoming SMS notifications!'
    # We need to keep communication with phone to get notifications
    thread = Thread(target = send_sms_prospera, args = (sm_item,idx ))
    thread.start()
    return

def test():
    # 14
    list_modem=[]
    sm_item = load_gsm(list_modem,11)
    sm_item = list_modem[0]
    idx = 7
    sm_item.SetIncomingCallback(sm_callback)
    try:
        sm_item.SetIncomingUSSD()
    except gammu.ERR_NOTSUPPORTED:
        print 'Your phone does not support incoming SMS notifications!'
    send_sms(sm_item, idx)

def main():
   load_all()
   for i in range(len(list_modem)):
        create_thread(list_modem[i], i)

   #Init prospera
   load_prospera()
   print ("Cargaron %d chips prospera"%(len(list_prospera)))
   for i in range(len(list_prospera)):
       create_prospera_thread(list_prospera[i], i)



main()
#test()
