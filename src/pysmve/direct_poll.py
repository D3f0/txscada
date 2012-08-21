# encoding: utf-8
'''
Poll UC directly
Show how to make direct poll of COMaster
'''

from socket import socket
from protocols.constructs import MaraFrame
from construct.lib.container import Container
from time import sleep


def main():
    while True:
        s = socket()
        s.connect(('192.168.1.97', 9761))
        paquete = MaraFrame.build(Container(
                                              source=64,
                                              dest=1,
                                              sequence=33,
                                              command=0x10,
                                              payload_10 = None
                                              ))
        print paquete, type(paquete)
        s.send(str(paquete))
        data = s.recv(1024)
        print MaraFrame.parse(data)
        sleep(1)
    
main()