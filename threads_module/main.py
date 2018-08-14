from threading import Thread
import inspect
import os, redis, requests,time,json, random, re, sys
from datetime import datetime
from gammu_load import *
##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants  import *
from callbacks import *
##########      Priority queues   ############
from PriorityQueue import PriorityQueue
############## Global variables ###############
MODEM_MAPING = [INCLUSION_MAPPING[modem]["number"] for modem in INCLUSION_MAPPING.keys()]
priority_queues = { i: PriorityQueue(i) for i in MODEM_MAPING}
conn = redis.Redis(REDIS_HOST)

def save_logs(idx,message,sent):
    """
    Function to record failed and sent messages

    :param idx: <int> queue idx
    :param message: <string> String with message value
    :param sent: <boolean> If the message was sent or not
    """
    print ("[LOG] %d %s %s"%(idx, message, sent))
    if sent:
        conn.incr("_"+str(idx)+"_sent_sms")
        conn.rpush("sent_message_"+str(idx), message)
    else:
        conn.incr("_"+str(idx)+"_failed_sms")
        conn.rpush("failed_message_"+str(idx),message)

def send_sms(sm_item, idx):
    """
    Main function of each thread. This function try to send a sms message
    through sm_item in a valid hour (range defined on constant file).

    :param sm_item: <gammu.StateMachine> proxy to connect with modem
    :param idx: <int> Idx of the priority_queue
    """
    while True:
        ###### Check if we can send messages ####
        if  int(datetime.now().strftime("%H")) < MAX_HOUR and \
            int(datetime.now().strftime("%H")) > MIN_HOUR:
            this_item = priority_queues[idx].pop()
            if this_item:
                data = json.loads(this_item)
                payload = {"Text": data["message"],
                          "SMSC": {"Location":1},
                          "Number": data["contact"]}

                try:
                    sm_item.SendSMS(payload)
                    #Add timestamp
                    data["sent_on"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    save_logs(idx, json.dumps(data),True)
                except gammu.GSMError:
                    data["counter"] = 1 + data["counter"] if "counter" in data else 1
                    if data["counter"] <= 4:
                        message_dump = json.dumps(data)
                        priority_queues[idx].push(message_dump, data["score"])
                    else:
                        data["sent_on"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                        save_logs(idx, json.dumps(data),False)
                if int(data["score"]) == HIGH_PRIORITY:
                    time.sleep(TIME_TO_SLEEP_HP)
                else:
                    time.sleep(TIME_TO_SLEEP_LP)
        else:
            try:
                status = sm_item.GetBatteryCharge()
            except:
                pass
            time.sleep(1)


def create_thread(sm_item, idx, function_callback):
    """
    Function to create a thread to send and receive sms

    :param sm_item: <gammu.StateMachine> proxy to connect with modem
    :param idx: <int> Idx of the priority_queue
    :param function_callback: <function> use this function to register as
                                         callback when modem receive a sms.
    """
    sm_item.SetIncomingCallback(function_callback)
    try:
        sm_item.SetIncomingSMS()
    except gammu.ERR_NOTSUPPORTED:
        print 'Your phone does not support incoming SMS notifications!'
    # We need to keep communication with phone to get notifications
    thread = Thread(target = send_sms, args = (sm_item, idx))
    thread.start()
    return

def main():
   #Init inclusion
   load_inclusion()
   for  item_modem,redis_idx, callback_f in zip(list_inclusion,INCLUSION_SLOTS, INCLUSION_CALLBACK):
       create_thread(item_modem,redis_idx, callback_f)

main()
