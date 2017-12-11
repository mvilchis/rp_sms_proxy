import time, redis, os
from grupo1 import grupo1
from grupo2 import grupo2
from grupo3 import grupo3
from grupo4 import grupo4
REDIS_HOST = 'localhost'


conn = redis.Redis(REDIS_HOST)

def add_to_redis(lista, queue):
    for item in lista:
        conn.set(item, {"channel":queue, "is_prospera": True})

def main():
    add_to_redis(g1,0)
    add_to_redis(g2,1)
    add_to_redis(g3,2)
    add_to_redis(g4,3)
