from threading import Thread
import os
import requests
from gammu_load import *

REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR','localhost')
conn = redis.Redis(REDIS_HOST)
RP_URL= os.getenv('RP_URL', "")

def sm_callback(sm, type, data):
    if not data.has_key('Number'):
        data = sm.GetSMS(data['Folder'], data['Location'])[0]
        payload={"backend":"Telcel",
                "sender":data['Number'],
                "message":data["Text"],
                "ts":"1",
                "id":"758af0a175f8a86"}
        r = requests.get(RP_URL, params = payload)
        break

def send_sms(sm_item, idx):
    while True:
        time.sleep(1)
        ######### Check if  have to send sms
        if conn.get(idx):
            data = json.loads(conn.lpop(idx))
            payload = {"Text": data["message"],"SMSC": {"Location":1},"Number": data["contact"]}
            try:
                sms_item.SendSMS(payload)
                return (True,payload)
            except gammu.GSMError:
                # Show error if message not sent
                print ('Error, SMS not Sent')
                return (False, payload)
        else:
            status = sm.GetBatteryCharge()
            time.sleep(1)


def create_thread(sm_item,idx):
    sm_item.SetIncomingCallback(sm_callback)
    try:
        sm_item.SetIncomingSMS()
    except gammu.ERR_NOTSUPPORTED:
        print 'Your phone does not support incoming SMS notifications!'
    # We need to keep communication with phone to get notifications
    thread = Thread(target = send_sms, args = (sm_item,idx ))
    thread.start()
    return

def test():
    # 14
    sm_item = list_modem[14]
    idx = 14
    sm_item.SetIncomingCallback(sm_callback)

    try:
        sm_item.SetIncomingSMS()
    except gammu.ERR_NOTSUPPORTED:
        print 'Your phone does not support incoming SMS notifications!'

    send_sms(sm_item, idx)

def main():
    for i in range(len(list_modem)):
        create_thread(list_modem[i], i)

test()
