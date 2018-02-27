from threading import Thread
import os, redis, requests,time,json, random, re
from datetime import datetime
import inspect, sys
##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants  import *

##################### Callback functions ########################

def sm_callback(sm, type, data):
    if not data.has_key('Number'):
        data = sm.GetSMS(data['Folder'], data['Location'])[0]
        #Now delete sms
        sm.DeleteSMS(Folder = data['Folder'], Location = data['Location'])
    #Only send message if is diferent to short numbers
    sender = data["Number"]
    if sender == "telcel" or sender =="movistar" or len(str(sender)) <=6:
        return
    payload={"backend":"Telcel",
                "sender":data['Number'],
                "message":data["Text"],
                "ts":"1",
                "id":"758af0a175f8a86"}
    return payload

###################################################################
#                       MISALUD CALLBACKS                         #
###################################################################

def callback_misalud_11(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["misalud_11"]["handler"], params = payload)

def callback_misalud_16(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["misalud_16"]["handler"], params = payload)


def callback_misalud_17(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["misalud_17"]["handler"], params = payload)

MISALUD_CALLBACK= [callback_misalud_11, callback_misalud_16, callback_misalud_17]

####################################################################
#                       INCLUSION CALLBACKS                        #
####################################################################

def callback_inclusion_4(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_4"]["handler"], params = payload)

def callback_inclusion_5(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_5"]["handler"], params = payload)

def callback_inclusion_6(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_6"]["handler"], params = payload)

def callback_inclusion_7(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_7"]["handler"], params = payload)

def callback_inclusion_12(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_12"]["handler"], params = payload)

def callback_inclusion_13(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_13"]["handler"], params = payload)

def callback_inclusion_14(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_14"]["handler"], params = payload)

def callback_inclusion_15(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_15"]["handler"], params = payload)

def callback_inclusion_20(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_20"]["handler"], params = payload)

def callback_inclusion_21(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["inclusion_21"]["handler"], params = payload)



INCLUSION_CALLBACK= [callback_inclusion_4
callback_inclusion_5,
callback_inclusion_6,
callback_inclusion_7,
callback_inclusion_12,
callback_inclusion_13,
callback_inclusion_14,
callback_inclusion_15,
callback_inclusion_20,
callback_inclusion_21]
