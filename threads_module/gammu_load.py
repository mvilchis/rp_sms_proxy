import gammu ,sys,os,inspect
##############     My constants     ##############
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Constants  import *


list_modem = []
list_prospera = []
def load_gsm(list_modem, idx):
    """ Load gsm slot to sistem """
    print("Entrando %d" % idx)
    item = gammu.StateMachine()
    print("Leera")
    item.ReadConfig(Filename="gammu_dir/"+str(idx)+".conf")
    print("Salida de leer")
    try:
        item.Init()
        list_modem.append(item)
        print ("%d agregado" % idx)
    except gammu.ERR_TIMEOUT:
        print ("Error timeout al intentar sincronizar  %d" % idx)
        return
    except gammu.ERR_DEVICEOPENERROR:
        print ("Error al intentar sincronizar %d" % idx)
        return
    print ("Salida")

def load_all():
    for i in MISALUD_SLOTS:
        load_gsm(list_modem, i)


def load_prospera():
    for i in PROSPERA_SLOTS:
        load_gsm(list_prospera, i)
