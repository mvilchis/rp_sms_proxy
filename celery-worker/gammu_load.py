import gammu

list_modem = []
def load_gsm(list_modem, idx):
    print("Entrando %d" % idx)
    item = gammu.StateMachine()
    print("Leera")
    item.ReadConfig(Filename="gammu/"+str(idx)+".conf")
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

for idx in range(23,24):
    load_gsm(list_modem, idx)
