import os
import configparser

config = configparser.ConfigParser()
config.read('../keys.ini', encoding='utf-8')
#############       General constants             ###############
DATE_FORMAT = "%d/%m/%Y-%H:%M"
MAX_TIME_RESPONSE = 300  # If contact send us a message before max_time
                          # We proccess their message with HIGH_PRIORITY
MAX_HOUR = 21
MIN_HOUR = 8
TIME_TO_SLEEP_HP = 20
TIME_TO_SLEEP_LP = 120
################ Rapidpro environment variables ################
RP_LAST_MESSAGES = config["rapidpro"]["RP_LAST_MESSAGES"]

####################      Mail environment      #################
EMAIL = config["email"]["USER"]
EMAIL_PASS = config["email"]["PASSWORD"]

##############     Read environment variables     ##############
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_URL = "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT)

#############     Configure celery beat          ###############
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Mexico_City'
LOW_PRIORITY = 1
HIGH_PRIORITY = 5

########################  Users to modem   ######################
INCLUSION_MODEM = "inclusion"

##################        Manage queues       ###################
INCLUSION_SLOTS = [5,6,7,13,14,15,20,21,0,1,2,3,8,9,10]

INCLUSION_MAPPING = {
    "inclusion_4" : {"number":4,  "handler":config["inclusion"]["HANDLER_4"]},
    "inclusion_5" : {"number":5,  "handler":config["inclusion"]["HANDLER_5"]},
    "inclusion_6" : {"number":6,  "handler":config["inclusion"]["HANDLER_6"]},
    "inclusion_7" : {"number":7,  "handler":config["inclusion"]["HANDLER_7"]},
    "inclusion_12": {"number":12, "handler":config["inclusion"]["HANDLER_12"]},
    "inclusion_13": {"number":13, "handler":config["inclusion"]["HANDLER_13"]},
    "inclusion_14": {"number":14, "handler":config["inclusion"]["HANDLER_14"]},
    "inclusion_15": {"number":15, "handler":config["inclusion"]["HANDLER_15"]},
    "inclusion_20": {"number":20, "handler":config["inclusion"]["HANDLER_20"]},
    "inclusion_21": {"number":21, "handler":config["inclusion"]["HANDLER_21"]},
    "inclusion_0": {"number":0, "handler":config["inclusion"]["HANDLER_0"]},
    "inclusion_1": {"number":1, "handler":config["inclusion"]["HANDLER_1"]},
    "inclusion_2": {"number":2, "handler":config["inclusion"]["HANDLER_2"]},
    "inclusion_3": {"number":3, "handler":config["inclusion"]["HANDLER_3"]},
    "inclusion_8": {"number":8, "handler":config["inclusion"]["HANDLER_8"]},
    "inclusion_9": {"number":9, "handler":config["inclusion"]["HANDLER_9"]},
    "inclusion_10": {"number":10, "handler":config["inclusion"]["HANDLER_10"]},
}

PHONE_TO_CALL_A = config["modem"]["PHONE_TO_CALL_A"]
PHONE_TO_CALL_B = config["modem"]["PHONE_TO_CALL_B"]


CEL_NUMBERS = {
 4: config["modem"]["phone_4"],
 5: config["modem"]["phone_5"],
 6: config["modem"]["phone_6"],
 7: config["modem"]["phone_7"],
12: config["modem"]["phone_12"],
13: config["modem"]["phone_13"],
14: config["modem"]["phone_14"],
15: config["modem"]["phone_15"],
20: config["modem"]["phone_20"],
21: config["modem"]["phone_21"],
0: config["modem"]["phone_0"],
1: config["modem"]["phone_1"],
2: config["modem"]["phone_2"],
3: config["modem"]["phone_3"],
8: config["modem"]["phone_8"],
9: config["modem"]["phone_9"],
10: config["modem"]["phone_10"],
}
