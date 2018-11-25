import inspect
import json
import os
import random
import re
import sys
import time
import redis
from celery import Celery
from datetime import datetime

import requests

from Constants import *

##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
conn = redis.Redis(REDIS_HOST)
celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

##################### Callback functions ########################

def sm_callback(sm, type, data):
    if not data.has_key('Number'):
        data = sm.GetSMS(data['Folder'], data['Location'])[0]
        #Now delete sms
        try:
            sm.DeleteSMS(Folder = data['Folder'], Location = data['Location'])
        except Exception,e:
            print str(e)
    #Only send message if is diferent to short numbers
    sender = data["Number"]
    if sender == "movistar" or not "Text" in data:
        return ""
    payload={"backend":"Telcel",
                "sender":data['Number'],
                "message":data["Text"],
                "ts":"1",
                "id":"758af0a175f8a86"}
    return payload

####################################################################
#                       INCLUSION CALLBACKS                        #
####################################################################

def callback_inclusion_4(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_4"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_5(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_5"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_6(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_6"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_7(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_7"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_12(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_12"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_13(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_13"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_14(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_14"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_15(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_15"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_20(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_20"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_21(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_21"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_0(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_0"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_1(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_1"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_2(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_2"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_3(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_3"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_8(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_8"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_9(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_9"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

def callback_inclusion_10(sm, type, data):
    payload = sm_callback(sm,type,data)
    if payload:
        r = requests.post(INCLUSION_MAPPING["inclusion_10"]["handler"], params = payload)
        print ("Respuesta %s" %(payload))

INCLUSION_CALLBACK={"5":callback_inclusion_5,
                    "6":callback_inclusion_6,
                    "7":callback_inclusion_7,
                    "13":callback_inclusion_13,
                    "14":callback_inclusion_14,
                    "15":callback_inclusion_15,
                    "20":callback_inclusion_20,
                    "21":callback_inclusion_21,
                    "0":callback_inclusion_0,
                    "1":callback_inclusion_1,
                    "2":callback_inclusion_2,
                    "3":callback_inclusion_3,
                    "8":callback_inclusion_8,
                    "9":callback_inclusion_9,
                    "10":callback_inclusion_10,
                    }
