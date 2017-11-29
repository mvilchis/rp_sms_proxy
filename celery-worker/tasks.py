import time, redis, os
import ast, json, requests, random
from celery import Celery
##########       Libraries mail    ###########
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
##########      Priority queues   ############
from rpq.RpqQueue import RpqQueue

################# Constants ##################
LIST_MODEM = 15

##########     Global variables     ##########
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
LIST_QUEUE = [RpqQueue(redis.StrictRedis(host=REDIS_HOST, port=6379, db=idx), 'simple_queue') for idx in range (1, 1+LIST_MODEM)]

conn = redis.Redis(REDIS_HOST)

redis_url = "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT)

CELERY_BROKER_URL=redis_url
CELERY_RESULT_BACKEND=redis_url
RP_MESSAGES= os.getenv('RP_MESSAGES', "")


celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

EMAIL=os.getenv('EMAIL','')
EMAIL_PASS=os.getenv('EMAIL_pass','')
server = smtplib.SMTP('smtp.gmail.com', 587)

@celery.task(name='tasks.request_to_rp')
def get_last_msgs():
    # Request all messages:
    resp = requests.get(url=RP_MESSAGES)
    data = json.loads(resp.text)

    for item in data['results']:
        contact_cel = item['contact']
        message = item['message']
        #### Redis ask to assign work
        if conn.get(contact_cel) is None:
            channel_queue = random.randint(0,LIST_MODEM-1)
            conn.set(contact_cel, channel_queue)
        else:
            channel_queue = conn.get(contact_cel)

        message = {"contact":contact_cel, "message": message}
        message_dump = json.dumps(message)

        if 'priority' in item:
            LIST_QUEUE[channel_queue].push(message_dump,100)
        else:
            LIST_QUEUE[channel_queue].push(message_dump,10)



@celery.task(name='tasks.send_ping')
def send_ping_task():
    for idx in range(LIST_MODEM):
        message = {"contact":"5521817435", "message": "ping desde %d" %(idx)}
        message_dump = json.dumps(message)
        LIST_QUEUE[idx].push(message_dump,100)



@celery.task(name='tasks.report_channels')
def report_channels_task():
    me = EMAIL
    you = "miguel.vilchis@datos.mx"

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
            </tr>
            <tr>
    """
    for idx in range(LIST_MODEM):
        html += """<tr>"""
        html +="""<td align="center">%d</td>""" %(idx)
        html +="""<td align="center">%d</td>"""%(conn.get(idx+"_sent_sms"))
        html +="""<td align="center">%d</td>""" %(conn.get(idx+"_failed_sms"))
        html +="""<td align="center">%d</td>"""%(LIST_QUEUE[idx].count())
        html += """</tr>"""
        conn.set(idx+"_sent_sms",0)
        conn.set(idx+"_failed_sms",0)
    html += """"</body></html>"""

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    server.sendmail(me, you, msg.as_string())
    server.quit()
