from threading import Thread
import os, redis, requests,time,json, random, re
from datetime import datetime

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

#Misalud callback
def callback_misalud_11(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["misalud_11"]["handler"], params = payload)

#Misalud callback
def callback_misalud_16(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["misalud_16"]["handler"], params = payload)

#Misalud callback
def callback_misalud_17(sm, type, data):
    payload = sm_callback(sm,type,data)
    r = requests.get(MISALUD_MAPPING["misalud_17"]["handler"], params = payload)

MISALUD_CALLBACK= [callback_misalud_11, callback_misalud_16, callback_misalud_17]
