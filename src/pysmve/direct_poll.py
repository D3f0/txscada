# encoding: utf-8

'''
Poll UC directly
Show how to make direct poll of COMaster
'''

from socket import socket
from protocols.constructs import MaraFrame
from construct.lib.container import Container
from time import sleep
from construct.core import FieldError
from protocols.constants import MAX_SEQ, MIN_SEQ
from datetime import datetime

def fecha():
    now = datetime.now()
    return now.strftime("%X us:") + "%d" % now.microsecond

def main():
    s = socket()
    s.connect(('192.168.1.97', 9761))
    output = Container(
                      source=64,
                      dest=1,
                      sequence=33,
                      command=0x10,
                      payload_10 = None)


    while True:
        print "-"*60
        print fecha()
        print "-"*60
        paquete = MaraFrame.build(output)
        #print paquete, type(paquete)
        s.send(str(paquete))
        data = s.recv(1024)
        try:
            data = MaraFrame.parse(data)
        except FieldError as e:
            print "Error al decodificar la trama", e
            continue
        MaraFrame.pretty_print(data,
                               show_header=False,
                               show_bcc=False)
        sleep(.8)
        output.sequence += 1
        if output.sequence > MAX_SEQ:
            output.sequence = MIN_SEQ
        #from IPython import embed; embed()

main()