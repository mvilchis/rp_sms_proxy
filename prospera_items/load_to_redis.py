import sys, redis, os,inspect, requests,json
from grupo1 import grupo1
from grupo2 import grupo2
from grupo3 import grupo3
from grupo4 import grupo4

##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants  import *

conn = redis.Redis(REDIS_HOST)

def add_to_redis(lista, queue):
    for item in lista:

        conn.set(item, {"channel":queue, "is_prospera": True})
        ### Only if is configurated
        if TOKEN_DASHBOARD and RP_URL_DASHBOARD:
            headers = {"Authorization": "Token "+TOKEN_DASHBOARD,
                    "Content-Type": "application/json"}
            data = {"contact":item ,
                "queue_number": queue,
                "is_prospera": True}
            requests.post(RP_URL_DASHBOARD+"add_contact/",data= json.dumps(data), headers = headers)

def main():
    add_to_redis(grupo1,PROSPERA_SLOTS[0])
    add_to_redis(grupo2,PROSPERA_SLOTS[1])
    add_to_redis(grupo3,PROSPERA_SLOTS[2])
    add_to_redis(grupo4,PROSPERA_SLOTS[3])
main()
