import time, redis, os,sys,inspect
import ast, json, requests, random
from celery import Celery
##########       Libraries mail    ###########
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
##########      Priority queues   ############
from rpq.RpqQueue import RpqQueue
##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants  import *


conn = redis.Redis(REDIS_HOST)
celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

def send_messages(data):
    for item in data:
        contact_cel = item['contact']
        message = item['message']
        queue = int(item['queue']) if 'queue' in item else ''
        #### Redis ask to assign work
        if conn.get(contact_cel) is None:
            new_idx = random.randint(0,len(MISALUD_SLOTS)-1)
            channel_queue = MISALUD_SLOTS[new_idx]

            conn.set(contact_cel, {"channel":channel_queue,
                                    "is_prospera": False})
            ############    Send info to dashboard
            headers = {"Authorization": "Token "+TOKEN_DASHBOARD,
                        "Content-Type": "application/json"}
            contact_data = {"contact":contact_cel ,
                            "queue_number": channel_queue,
                            "is_prospera": False
                            }
            if TOKEN_DASHBOARD and RP_URL_DASHBOARD:
                requests.post(RP_URL_DASHBOARD+"add_contact/",data= json.dumps(contact_data), headers = headers)
            else: #Save to on localhost
                conn.rpush("add_contact",contact_data)
        else:
            if queue:
                channel_queue = queue
            else:
                contact_data = ast.literal_eval(conn.get(contact_cel))
                channel_queue =contact_data["channel"]
            message = {"contact":contact_cel, "message": message}
            message_dump = json.dumps(message)
            conn.rpush(channel_queue, message_dump)


@celery.task(name='tasks.request_to_rp')
def get_last_msgs():
    # Request all messages:
    resp = requests.get(url=RP_LAST_MESSAGES)
    data = json.loads(resp.text)
    send_messages(data['results'])


@celery.task(name='tasks.request_to_dashboard')
def get_resend_dashboard():
    if TOKEN_DASHBOARD and RP_URL_DASHBOARD:
        resp = requests.get(url = RP_URL_DASHBOARD+"add_message/R/")
        data = json.loads(resp.text)
        send_messages([{"message":item["message"],"queue":item["queue_number"],"contact":item["contact_number"]}for item in data])


@celery.task(name='tasks.request_ping_dashboard')
def get_ping_dashboard():
    if TOKEN_DASHBOARD and RP_URL_DASHBOARD:
        resp = requests.get(url = RP_URL_DASHBOARD+"show_ping/")
        data = json.loads(resp.text)
        for number in data['numbers']:
            send_ping_task(contact = number)

@celery.task(name='tasks.send_ping')
def send_ping_task(contact = "5521817435"):
    for idx in MISALUD_SLOTS:
        message = {"contact":contact, "message": "ping desde %d" %(idx)}
        message_dump = json.dumps(message)
        conn.rpush(idx, message_dump)
    send_ping_prospera(contact)


def send_ping_prospera(contact):
    for idx in PROSPERA_SLOTS:
        message = {"contact":contact, "message": "ping desde %d" %(idx)}
        message_dump = json.dumps(message)
        conn.rpush(idx, message_dump)

@celery.task(name='tasks.report_channels')
def report_channels_task():
    me = EMAIL
    you = "miguel.vilchis@datos.mx"
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
    for idx in MISALUD_SLOTS:
        html += """<tr>"""
        html +="""<td align="center">%d</td>""" %(idx)
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_sent_sms"))
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_failed_sms"))
        html +="""<td align="center">%d</td>"""%(LIST_QUEUE[idx].count())
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_not_sent_sms"))
        html += """</tr>"""
        conn.set("_"+str(idx)+"_sent_sms",0)
        conn.set("_"+str(idx)+"_failed_sms",0)
        conn.set("_"+str(idx)+"_not_sent_sms",0)


    for idx in PROSPERA_SLOTS:
        html += """<tr>"""
        html +="""<td align="center">%d</td>""" %(idx)
        html +="""<td align="center">%s</td>"""% (conn.get("_"+str(idx)+"_sent_sms_prospera"))
        html +="""<td align="center">%s</td>""" %(conn.get("_"+str(idx)+"_failed_sms_prospera"))
        html +="""<td align="center">%d</td>"""%(conn.llen(idx))
        html +="""<td align="center">%s</td>""" %(conn.get("_"+str(idx)+"_not_sent_sms_prospera"))
        html += """</tr>"""
        conn.set("_"+str(idx)+"_sent_sms_prospera",0)
        conn.set("_"+str(idx)+"_failed_sms_prospera",0)
        conn.set("_"+str(idx)+"_not_sent_sms_prospera",0)

    html += """"</body></html>"""

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    server.sendmail(me, you, msg.as_string())
    server.quit()
