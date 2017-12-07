import gammu ,sys

list_modem = []
def load_gsm(list_modem, idx):
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
    for i in range(0,4):
        load_gsm(list_modem, i)
    for i in range(8,12):
        load_gsm(list_modem, i)
    for i in range(16,20):
        load_gsm(list_modem, i)
    load_gsm(list_modem, 24)
    for i in range(26,28):
        load_gsm(list_modem, i)



