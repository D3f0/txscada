#! /usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Este módulo funciona como emulador de concentrador.
Está basado en la clase PicnetProtocol y funciona como servidor.
'''

#TODO: Utilizar el modulo conf

import sys
sys.path.append('..')

#from twisted.internet.protocol import Factory
from twisted.internet import reactor
from pyscada.protocol import PicnetProtocolFactory, PicnetProtocol
from twisted.python import log
from random import randint
from picnet.event import EventoCodigo
from datetime import datetime
import itertools
from random import randrange
import time
from picnet.bitfield import bitfield

class Movimiento(object):
    def __init__(self,lista,offset, delay = -1):
        ''' Emula un movimiento 
        @param lista: Lista de valores por los cuales ciclar
        @param offset: Posicion en la lista por la cual empezar
        @param delay: Tiempo de retardo de cambio
        '''
        self.lista = lista
        if offset < len(lista):
            self.i = offset
        else:
            self.i = 0
        # TODO: Implementar
        self.delay = delay
        
    def __call__(self):
        a = self.i
        self.i = self.i < (len(self.lista)-1) and (self.i+1) or 0
        return self.lista[a]
        

def iter_forever(num):
    for i in itertools.cycle(xrange(num)):
        yield i

class MockingServerProtocol(PicnetProtocol):
    # UC ID que generan timeout
    GENERATE_TIEMOUT = []
    
    def __init__(self, *largs, **kwargs):
        lista = [0,1]
        for i in range(0,9):
            setattr(self, 'mov%d' % i, Movimiento(lista, i % len(lista) ))
                
        
    def packageRecieved(self, pkg):
        if pkg.DST in self.GENERATE_TIEMOUT:
            return
        
        if pkg.COM == 0:
            # Simulamos el timepo que tarda la aplicación
            tiempo = randrange(1, 250, 1) * 0.001
            reactor.callLater( tiempo, self.do_reply, pkg, time.time())
            
    
            
    def do_reply(self, pkg, t_inicio):
        log.msg('Respuesta a Peticion de estados y eventos luego de %.5f' % (time.time() - t_inicio))
        bf1 = bitfield(0)
        bf1[0:2] = self.mov0()
        bf1[2:4] = self.mov1()
        #bf1[4:6] = self.mov2()
        #bf1[6:8] = self.mov3()
        
        bf2 = bitfield(0)
        #bf2[0:2] = self.mov4()
        #bf2[2:4] = self.mov5()
        #bf2[4:6] = self.mov6()
        
        bf3 = bitfield(0)
        #bf3[4:6] = self.mov7()
        #bf3[2:4] = self.mov8()
        #bf3[0:2] = self.mov9()
        
        
        # Generamos el payload
        payload = [0x03, # 2 de Variables de estado 
                     0xf3, 0x3a,
                     
                     0x05,  # 4 de DI
                     int(bf1),
                     int(bf2),
                     int(bf3),
                     255,
                     
                     0x05,  # 2 analogicas de 2 bytes
                     randint(0,3), randint(0,255),
                     randint(0,3), randint(0,255),
                    ]
        
        cnt_events = randint(0, 4)
        
        for _ in range(cnt_events):
            ints = EventoCodigo.create_ints(tipo = randint(0,2),
                                            prio = randint(0,2),
                                            codigo = randint(0,16),
                                            port = randint(0,63),
                                            bit = randint(0,8),
                                            status = randint(0,1),
                                            date_time=datetime.now(),
                                            cseg = randint(0,99),
                                            dmseg = randint(0,99),
                                            )
            payload += ints
        resp = pkg.response(payload)
        print "Size final: %d, cantidad de eventos %d" % (len(payload), cnt_events)
        print "Enviando payload", resp.get_payload()
        print "Paquete a enviar:", ' '.join(( ("%.2x" % ord(c)).upper() for c in resp.octet_str()))
        self.transport.write(resp.octet_str())
        
        
class PicnetMockingServerFacotry(PicnetProtocolFactory):
    protocol = MockingServerProtocol


if __name__ == "__main__":
    '''
    Programa de prueba
    '''
    log.startLogging(sys.stdout, setStdout=False)
    reactor.listenTCP(9761, PicnetMockingServerFacotry())
    reactor.run()
