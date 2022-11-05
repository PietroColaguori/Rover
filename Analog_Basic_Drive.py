#Created by Kepler Electronics, https://www.youtube.com/keplerelectronics
#nella descrizione del video c'è un sacco di materiale, dai prodotti usati al codice e librerie

"""
Controllare tramite le levette analogiche di un controller Bluetooth i motori, controllati da un PI Moroni Explorer.
NB: verificare che funzioni per più di 2 motori. Nel caso penso si possano prendere altri "motor controllers" abilitati
    per il numero di motori richiesto.

1. Prima di fare il pairing quindi runniamo il comando "ls /dev/input" per scoprire i devices connessi al raspberry 
(formato: "eventI", i-esimo device). Avviamo il pairing e ri-eseguiamo il comando, sarà comparso un nuovo event con l'id associato 
al nostro controller, è importante conoscerlo per testare.

2. Importiamo la libreria "evdev" e runniamo il comando:
    "python /usr/local/lib/python<numeroVersione>/dist-packages/evdev/evtest-py"
    Muoviamo gli analogici e verificheremo a che movimento è associato quale numero.
    I valori da bottone sono identificato da "EV_KEY", quelli analogici da "EV_ABS".

3. Dopo aver testato il codice la prima volta è importante settarne l'avvio al boot, per evitare di dover usare tastiera/mouse/monitor.
    Salvare programma in /home/pi, al suo interno "sudo nano /home/pi/.bashrc" ed alla fine del bash rc file ed aggiungere le 2 righe:
    "echo Running at boot"
    "sudo python /home/pi/Analog_Basic_Drive.py &"
    Salvare e fare il reboot per verificare che il programma sia avvii al boot.

4. Se non si vogliono usare altri devices connessi al raspberry (solo il controller), nel codice scriviamo "fh = open('.../event0')",
   come è già fatto nell'esempio, normalmente per il testing iniziale al posto di 0 ci sarà l'ID individuato al passo 1. 
   In generale usiamo eventX con X=k+1 e k = numero devices connessi al raspberry prima del pairing.

Qui sembra che siano usati 2 motori, bisognerà vedere come modificare il codice per adattarsi all'hardware.

"""

import explorerhat  #motor control (solo per Linux (?))
import time         #delays and wait commands
explorerhat.motor.one.invert()  #si inverte perché i motori sono invertiti nel corpo del rover (?)

from evdev import InputDevice, ecodes  #per leggere l'input proveniente dal controller
while 1==1:  #controlla costantemente la presenza del controller
    try:
        fh = open('/dev/input/event0')  #cerca input, event0 vuol dire che nulla è ancora connesso, eventX => X oggetti connessi
        print('controller found')
        gamepad = InputDevice('/dev/input/event0')  #controller trovato
        print(gamepad)  #stampa identificativo controller trovato

        for event in gamepad.read_loop():  #loop che controlla costantemente cosa viene premuto sul controller
            if event.type == ecodes.EV_ABS:  #valore assoluto restituito dal controller -> valore analogico (leva di sx o dx)
                if event.code == 5:  #è stata mossa la leva di destra (dipende dal dispositivo)
                    #viene creata una deadzone tra 100 e 155, se input in [100, 155] non succede nulla
                    #questo è utile per evitare che il "controller drifting" ed evitare che il rover si muova
                    #anche quando non viene dato nessun input dal controller
                    #nel caso del tutorial, tirare la leva tutta in alto restituisce 255, in basso 0
                    if event.value > 155:  #vai avanti
                        explorerhat.motor.one.forwards(event.value-155)    #explorerhat accetta valori di velocità in [0, 100]
                    elif event.value < 100:  #vai indietro
                        explorerhat.motor.one.backwards((100-event.value)) #explorerhat accetta valori di velocità in [0, 100]
                    else:
                        explorerhat.motor.one.stop()  #ferma il motore se nella deadzone
                elif event.code == 1:  #è stata mossa la leva di sinistra (dipende dal dispositivo)
                    if event.value > 155:
                        explorerhat.motor.two.forwards(event.value-155)
                    elif event.value < 100:
                        explorerhat.motor.two.backwards((100-event.value))
                    else:
                        explorerhat.motor.two.stop()
    except IOError:
        time.sleep(1)  #se non trova un device, aspetta un minuto e riprova
        print('Controller Not Found')
