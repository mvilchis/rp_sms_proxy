import time, redis, os,sys,inspect
import ast, json, requests, random
from celery import Celery
##########       Libraries mail    ###########
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
        org = item['org']
        queue = int(item['queue']) if 'queue' in item else ''
        modem = item['modem']
        #### Redis ask to assign work
        if not modem:
            if org == MISALUD_MODEM:
                new_idx = random.randint(0,len(MISALUD_SLOTS)-1)
                channel_queue = MISALUD_SLOTS[new_idx]
                conn.set(contact_cel, {"channel":channel_queue,
                                    "is_prospera": False})
            else:
                new_idx = random.randint(0,len(INCLUSION_SLOTS)-1)
                channel_queue = INCLUSION_SLOTS[new_idx]
                conn.set(contact_cel, {"channel":channel_queue,
                                    "is_prospera": False})

        else:
            message = {"contact":contact_cel, "message": message}
            message_dump = json.dumps(message)
            queue = ""
            if modem in INCLUSION_MAPPING:
                queue = INCLUSION_MAPPING[modem]["number"]
            elif modem in MISALUD_MAPPING:
                queue = MISALUD_MAPPING[modem]["number"]
            elif modem in PROSPERA_MAPPING:
                queue = PROSPERA_MAPPING[modem]["number"]
            else:
                print ("Sin modem")
                print (data)
            if queue:
                conn.rpush(queue, message_dump)


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
        message = {"contact":contact, "message": "ping misalud desde %d" %(idx)}
        message_dump = json.dumps(message)
        conn.rpush(idx, message_dump)
    send_ping_prospera(contact)
    send_ping_inclusion(contact)


def send_ping_prospera(contact):
    for idx in PROSPERA_SLOTS:
        message = {"contact":contact, "message": "ping prospera desde %d" %(idx)}
        message_dump = json.dumps(message)
        conn.rpush(idx, message_dump)

def send_ping_inclusion(contact):
    for idx in INCLUSION_SLOTS:
        message = {"contact":contact, "message": "ping inclusion desde %d" %(idx)}
        message_dump = json.dumps(message)
        conn.rpush(idx, message_dump)


@celery.task(name='tasks.report_inclusion')
def report_inclusion_task():
    ### Create csv
    failed_msgs = ""
    send_msgs = ""
    for idx in INCLUSION_SLOTS:
        for i in range(conn.llen("failed_message_"+str(idx))):
            data = json.loads(conn.lpop("failed_message_"+str(idx)))
            failed_msgs+= data["contact"]+","+data["message"]+"\n"
        for i in range(conn.llen("sent_message_"+str(idx))):
            data = json.loads(conn.lpop("sent_message_"+str(idx)))
            send_msgs+= data["contact"]+","+data["message"]+"\n"
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
            html +="""<td align="center">%d</td>"""%(conn.llen(idx))
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
        html +="""<td align="center">%d</td>"""%(conn.llen(idx))
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_not_sent_sms"))
        html += """</tr>"""
        conn.set("_"+str(idx)+"_sent_sms",0)
        conn.set("_"+str(idx)+"_failed_sms",0)
        conn.set("_"+str(idx)+"_not_sent_sms",0)


    for idx in PROSPERA_SLOTS:
        html += """<tr>"""
        html +="""<td align="center">%d</td>""" %(idx)
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_sent_sms"))
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_failed_sms"))
        html +="""<td align="center">%d</td>"""%(conn.llen(idx))
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_not_sent_sms"))
        html += """</tr>"""
        conn.set("_"+str(idx)+"_sent_sms",0)
        conn.set("_"+str(idx)+"_failed_sms",0)
        conn.set("_"+str(idx)+"_not_sent_sms",0)

    for idx in INCLUSION_SLOTS:
        html += """<tr>"""
        html +="""<td align="center">%d</td>""" %(idx)
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_sent_sms"))
        html +="""<td align="center">%s</td>"""%(conn.get("_"+str(idx)+"_failed_sms"))
        html +="""<td align="center">%d</td>"""%(conn.llen(idx))
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
    server.sendmail(me, you, msg.as_string())
    server.quit()
