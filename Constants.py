import os

################ Rapidpro environment variables ################
RP_URL_DASHBOARD= os.getenv('RP_URL_DASHBOARD', "")
TOKEN_DASHBOARD = os.getenv('TOKEN_DASHBOARD', "")
RP_URL= os.getenv('RP_URL', "")
RP_URL_PROSPERA= os.getenv('RP_URL_PROSPERA', "")
RP_LAST_MESSAGES= os.getenv('RP_LAST_MESSAGES', "")

####################      Mail environment      #################
EMAIL=os.getenv('EMAIL','')
EMAIL_PASS=os.getenv('EMAIL_PASS','')

##############     Read environment variables     ##############
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_URL = "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT)

#############     Configure celery beat          ###############
CELERY_BROKER_URL=REDIS_URL
CELERY_RESULT_BACKEND=REDIS_URL
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Mexico_City'

##################        Manage queues       ###################
PROSPERA_SLOTS = [0,1,2,3]
MISALUD_SLOTS = [8,9,10,11,16]




########## Localhost ################
RP_URL_DASHBOARD = "http://127.0.0.1:8000/"
TOKEN_DASHBOARD= "c39f01ce09ce3fb0b28a79a00d42357ca38cfedc"
