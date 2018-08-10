import os
import configparser

config = configparser.ConfigParser()
config.read('keys.ini', encoding='utf-8')

#############       General constants             ###############
DATE_FORMAT = "%d/%m/%Y-%H:%M"
MAX_TIME_RESPONSE = 1440  # If contact send us a message before max_time
                          # We proccess their message with HIGH_PRIORITY
MAX_HOUR = 19
MIN_HOUR = 9
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
INCLUSION_SLOTS = [4,5,6,7,12]

INCLUSION_MAPPING = {
    "inclusion_4" : {"number":4,  "handler":config["inclusion"][HANDLER_4]},
    "inclusion_5" : {"number":5,  "handler":config["inclusion"][HANDLER_5]},
    "inclusion_6" : {"number":6,  "handler":config["inclusion"][HANDLER_6]},
    "inclusion_7" : {"number":7,  "handler":config["inclusion"][HANDLER_7]},
    "inclusion_12": {"number":12, "handler":config["inclusion"][HANDLER_12]},
}
