from threading import Thread
import os, redis, requests,time,json, random, re
from datetime import datetime
##########      Priority queues   ############
from rpq.RpqQueue import RpqQueue

from gammu_load import *
##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants  import *
from callbacks import *
############## Global variables ###############
conn = redis.Redis(REDIS_HOST)


def send_sms(sm_item, idx):
    while True:
        ######### Check if  have to send sms
        if conn.llen(idx) > 0:
            for i in range(conn.llen(idx)):
                data = json.loads(conn.lpop(idx))
                if data["contact"] == "movistar":
                    continue
                if idx in PROSPERA_SLOTS or idx in INCLUSION_SLOTS:
                    time.sleep(20)
                payload = {"Text": data["message"],"SMSC": {"Location":1},"Number": data["contact"]}
                try:
                    sm_item.SendSMS(payload)
                    ###### Add message success to redis #####
                    conn.incr("_"+str(idx)+"_sent_sms")
                    conn.rpush("sent_message_"+str(idx),json.dumps(data))
                except gammu.GSMError:
                    try_on_queue = ''
                    data["counter"] = 1 + data["counter"] if "counter" in data else 1
                    if data["counter"] ==4: #### Sleep 2 seconds to reconect with modem
                        time.sleep(2)
                    if not try_on_queue:
                        try_on_queue = idx

                    if data["counter"] <= 4: #Only try to resend three times
                        message_dump = json.dumps(data)
                        conn.rpush(try_on_queue,message_dump)
                    else:
                        conn.rpush("failed_message_"+str(idx),json.dumps(data))
                        print ('Error, SMS not SENT en canal %d' %idx)
                        print (data)
                        conn.incr("_"+str(idx)+"_failed_sms")
        else:
           try:
                status = sm_item.GetBatteryCharge()
           except:
                pass
           time.sleep(1)


def create_thread(sm_item,idx, function_callback):
    sm_item.SetIncomingCallback(function_callback)
    try:
        sm_item.SetIncomingSMS()
    except gammu.ERR_NOTSUPPORTED:
        print 'Your phone does not support incoming SMS notifications!'
    # We need to keep communication with phone to get notifications
    thread = Thread(target = send_sms, args = (sm_item,idx ))
    thread.start()
    return



def main():
   #Init inclusion
   load_inclusion()
   for  item_modem,redis_idx, callback_f in zip(list_inclusion,INCLUSION_SLOTS, INCLUSION_CALLBACK):
       create_thread(item_modem,redis_idx, callback_f)


   load_all()
   for  item_modem,redis_idx, callback_f in zip(list_modem,MISALUD_SLOTS, MISALUD_CALLBACK):
        create_thread(item_modem,redis_idx, callback_f)

   #Init prospera
   load_prospera()
   print ("Cargaron %d chips prospera"%(len(list_prospera)))
   for  item_modem,redis_idx,callback_f in zip(list_prospera,PROSPERA_SLOTS,PROSPERA_CALLBACK):
       create_thread(item_modem,redis_idx, callback_f)



main()
#test()
