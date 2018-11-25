from threading import Thread
import inspect
import random
import argparse
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


ap = argparse.ArgumentParser()
ap.add_argument("-s", "--slots", required=False,
        help="slots to work with")
args = vars(ap.parse_args())


def save_logs(idx,message,sent):
    """
    Function to record failed and sent messages

    :param idx: <int> queue idx
    :param message: <string> String with message value
    :param sent: <boolean> If the message was sent or not
    """
    with open("modem.logs", "a") as myfile:
        myfile.write("[LOG %d][%s] %s\n"%(idx,sent, message))

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
        print ("Hola %d" %(idx))
        ###### Check if we can send messages ####
        if  int(datetime.now().strftime("%H")) < MAX_HOUR and \
            int(datetime.now().strftime("%H")) > MIN_HOUR:

            this_item = priority_queues[idx].pop()
            if this_item:
                data = json.loads(this_item)
                print (data)
                payload = {"Text": data["message"],
                          "SMSC": {"Number":CEL_NUMBERS[idx]},
                          "Number": data["contact"]}
                if int(data["score"]) == HIGH_PRIORITY:
                    for i in range(TIME_TO_SLEEP_HP):
                        try:
                            status = sm_item.GetBatteryCharge()
                            signal = sm_item.GetSignalQuality()
                        except:
                            pass
                        time.sleep(1)
                else:
                    for i in range(TIME_TO_SLEEP_LP + random.randrange(0,30)):
                        print("Sleep %d %d" %(i, idx))
                        try:
                            status = sm_item.GetBatteryCharge()
                            signal = sm_item.GetSignalQuality()
                        except:
                            pass
                        time.sleep(1)
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
            else:
                try:
                    status = sm_item.GetBatteryCharge()
                    signal = sm_item.GetSignalQuality()
                except:
                    pass
                time.sleep(1)
        else:
            try:
                status = sm_item.GetBatteryCharge()
                signal = sm_item.GetSignalQuality()
            except:
                pass
            time.sleep(1)

def make_call(sm_item, idx):
    """
    Call function of each thread. This function try to call a user
    through sm_item.

    :param sm_item: <gammu.StateMachine> proxy to connect with modem
    :param idx: <int> Idx of the priority_queue
    """
    while True:
        if conn.get(str(idx)+"_call_now") == "1":
            conn.set(str(idx)+"_call_now", "0")
            try:
                if int(idx)%2 == 0:
                    sm_item.DialVoice(PHONE_TO_CALL_A)
                else:
                    sm_item.DialVoice(PHONE_TO_CALL_B)
            except:
                print ("Fallo llamada en slot %s" %(str(idx)))

def try_enable(call, name):
    try:
        call()
    except gammu.ERR_NOTSUPPORTED:
        print('{0} notification is not supported.'.format(name))
    except gammu.ERR_SOURCENOTAVAILABLE:
        print('{0} notification is not enabled in Gammu.'.format(name))
    except:
        print ("Error pero continuamos")

def create_thread(sm_item, idx, function_callback):
    """
    Function to create a thread to send and receive sms

    :param sm_item: <gammu.StateMachine> proxy to connect with modem
    :param idx: <int> Idx of the priority_queue
    :param function_callback: <function> use this function to register as
                                         callback when modem receive a sms.
    """
    sm_item.SetIncomingCallback(function_callback)
    # Enable notifications from calls
    try_enable(sm_item.SetIncomingSMS, 'Incoming SMS')
    # Enable notifications for incoming USSD
    try_enable(sm_item.SetIncomingUSSD, 'Incoming USSD')
    # We need to keep communication with phone to get notifications
    print ("Start thread %d" %(idx))
    thread_1 = Thread(target = send_sms, args = (sm_item, idx))
    thread_1.start()
    #thread_2 = Thread(target = make_call, args = (sm_item, idx))
    #thread_2.start()
    print ("Thread ready %d" %(idx))
    return

def main():
    slots = json.loads(args["slots"])
    valid_slots = INCLUSION_SLOTS
    callbacks = INCLUSION_CALLBACK.values()
    if slots:
        valid_slots = [i for i in slots if i in INCLUSION_SLOTS]
        callbacks = [INCLUSION_CALLBACK[i] for i in valid_slots]

    #Init inclusion
    load_inclusion(valid_slots)

   for  item_modem,redis_idx, callback_f in zip(list_inclusion,valid_slots, callbacks):
       print ("Carga %d" %(redis_idx))
       create_thread(item_modem,redis_idx, callback_f)
   print "Fin de carga"
main()
