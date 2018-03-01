import os

################ Rapidpro environment variables ################
RP_URL_DASHBOARD= os.getenv('RP_URL_DASHBOARD', "")
TOKEN_DASHBOARD = os.getenv('TOKEN_DASHBOARD', "")
RP_URL= os.getenv('RP_URL', "")
RP_URL_PROSPERA= os.getenv('RP_URL_PROSPERA', "")
RP_URL_INCLUSION=os.getenv('RP_URL_INCLUSION', "https://rapidpro.datos.gob.mx/c/kn/25c52773-2f16-481f-9572-3bb01df30dac/receive")
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

########################  Users to modem   ######################
MISALUD_MODEM="misalud"
PROSPERA_MODEM="prospera"
INCLUSION_MODEM="inclusion"

##################        Manage queues       ###################
PROSPERA_SLOTS = [0,1,2,3,8,9,10]
MISALUD_SLOTS = [11,16,17]
INCLUSION_SLOTS =[4,5,6,7,12,13,14,15,20,21]
