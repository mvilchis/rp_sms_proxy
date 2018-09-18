import ast
import inspect
import json
import mimetypes
import os
import random
import redis
from datetime import datetime
##########       Libraries mail    ###########
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from celery import Celery


##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants import *
from PriorityQueue import PriorityQueue

##############    PriorityQueues    ##############
MODEM_MAPING = [INCLUSION_MAPPING[modem]["number"] for modem in INCLUSION_MAPPING.keys()]
priority_queues = { i: PriorityQueue(i) for i in MODEM_MAPING}
conn = redis.Redis(REDIS_HOST)
celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


def send_messages(data):
    for item in data:
        contact_cel = item['contact']
        message = item['message']
        org = item['org']
        queue = int(item['queue']) if 'queue' in item else ''
        modem = item['modem']
        #### Redis ask to assign work
        if not modem:
            conn.rpush("sin_modem", json.dumps(data))
        else:
            score = LOW_PRIORITY
            if conn.get(contact_cel):
                last_message_time = datetime.strptime(conn.get(contact_cel),
                                                      DATE_FORMAT)
                time_delta = datetime.now()-last_message_time
                minutes = (time_delta).total_seconds() / 60
                if minutes < MAX_TIME_RESPONSE:
                    score = HIGH_PRIORITY
            message = {"contact":contact_cel, "message": message, "score":score}
            message_dump = json.dumps(message)
            queue = ""
            if modem in INCLUSION_MAPPING:
                queue = INCLUSION_MAPPING[modem]["number"]
            else:
                print ("Sin modem")
                print (data)
            if queue:
                #Determine the propority:
                conn.set(contact_cel, datetime.now().strftime(DATE_FORMAT))
                priority_queues[queue].push(message_dump, score)


@celery.task(name='tasks.request_to_rp')
def get_last_msgs():
    # Request all messages:
    try:
        resp = requests.get(url=RP_LAST_MESSAGES)
        data = json.loads(resp.text)
        send_messages(data['results'])
    except Exception as e:
        print ("[ERROR] in get_last_msgs")
        print (e)


@celery.task(name='tasks.send_ping')
def send_ping_task(contact = "5521817435"):
    for idx in INCLUSION_SLOTS:
        message = {"contact":contact,
                   "message": "ping misalud desde %d" %(idx),
                   "score": HIGH_PRIORITY}
        message_dump = json.dumps(message)
        priority_queues[idx].push(message_dump, HIGH_PRIORITY)


@celery.task(name='tasks.report_inclusion')
def report_inclusion_task():
    ### Create csv
    failed_msgs = "Contacto, Mensaje, Ultimo intento\n"
    send_msgs = "Contacto, Mensaje, Hora de envio\n"
    for idx in INCLUSION_SLOTS:
        for i in range(conn.llen("failed_message_"+str(idx))):
            data = json.loads(conn.lpop("failed_message_"+str(idx)))
            failed_msgs+= data["contact"]+","+data["message"]+","+data["sent_on"]+","+str(data["score"])+"\n"
        for i in range(conn.llen("sent_message_"+str(idx))):
            data = json.loads(conn.lpop("sent_message_"+str(idx)))
            send_msgs+= data["contact"]+","+data["message"]+","+data["sent_on"]+","+str(data["score"])+"\n"
    failed_csv = open('failed_msgs.csv', 'w')
    failed_csv.write(failed_msgs)
    failed_csv.close()
    send_csv = open('sent_msgs.csv', 'w')
    send_csv.write(send_msgs)
    send_csv.close()
    for you in ["miguel.vilchis@datos.mx","alexis.cherem@datos.mx"]:
        me = EMAIL
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.ehlo()
        server.login(EMAIL, EMAIL_PASS)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Reporte GSM modem"
        msg['From'] = EMAIL
        msg['To'] = you
        text = "Va el reporte del modem gms"

        html = """\
        <html>
            <head></head>
            <body>
                <table style="width:80%;" >
                <tr>
                    <th>Canal</th>
                    <th>Mensajes enviados</th>
                    <th>Mensajes fallidos</th>
                    <th>Mensajes encolados</th>
                    <th>Mensajes no enviados</th>
                </tr>
                <tr>
        """
        for idx in INCLUSION_SLOTS:
            html += """<tr>"""
            html +="""<td align="center">%d</td>""" %(idx)
            html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_sent_sms"))
            html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_failed_sms"))
            html +="""<td align="center">%d</td>"""%(priority_queues[idx].len())
            html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_not_sent_sms"))
            html += """</tr>"""
            conn.set("_"+str(idx)+"_sent_sms",0)
            conn.set("_"+str(idx)+"_failed_sms",0)
            conn.set("_"+str(idx)+"_not_sent_sms",0)

        html += """</body></html>"""

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        ##################  File #######################
        for fileToSend in ["sent_msgs.csv", "failed_msgs.csv"]:
            ctype, encoding = mimetypes.guess_type(fileToSend)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            fp = open(fileToSend)
            attachment = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
            attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
            msg.attach(attachment)
        server.sendmail(me, you, msg.as_string())
        server.quit()
