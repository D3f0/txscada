#! /usr/bin/env python
# -*- encoding: utf-8 -*-
__doc__ = \
'''
    Core del daemon de adquisición de datos.
'''
import sys
sys.path.insert(0, '..')

try:
    import picnet
except:
    print "No puede encontrar picnet"
    sys.exit(0)

from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Thread
from django.core.management import setup_environ 
from socket import socket
from socket import SHUT_RD, SHUT_RDWR, SHUT_WR
from socket import error as SocketError
from picnet import proto 
from picnet.proto import Paquete
from picnet.proto import MIN_SEQ, MAX_SEQ
from picnet.automata import UCNetPacketDetector


import time
from Queue import Queue


#===============================================================================
# Bandera globar de interrupcion para los hilos de concentradores
#===============================================================================
GLOBAL_INTERRUPT_FLAG = False
    
def request_shutdown():
    print "Peticion de cierre"
    # TODO: Implementarlo mejor
    sys.exit(3)
    

class XMLRPCThread(Thread):
    def __init__(self, host, port):
        '''
        Constructor, crea la instancia del servidor
        '''
        Thread.__init__(self)
        self.server = SimpleXMLRPCServer((host, port))
            
    def run(self):
        # Se supone que aca tenemos la intefase de control del scada
        self.server.serve_forever()

class ConcentradorThread(Thread):
    # Atributo de clase para detener a los hilos
    # cuando se desea finalizar le programa
    stop_flag = False
    # Cola para sincornizacion
    queue = Queue()
    
    def __init__(self, concentrador):
        Thread.__init__(self)
        self.concentrador = concentrador
        self.seq_num = MIN_SEQ
        self.socket = None
        # Comienzo de la rutinaSHUT_RD
        self.setDaemon(True)
        self.start()
        
    
    def _connect(self):
        ''' Conectar con el concentrador '''
        tries = 3   # Intentos, hardcodeado
        if self.socket:
            self.socket.close()
        # Creamos el socket
        self.socket = socket()
        self.socket.settimeout(3)
        while tries:
            try:
                print self.concentrador.ip_address
                self.socket.connect((self.concentrador.ip_address, 
                                     proto.TCP_PORT))
            except SocketError, e:
                print "Timeout! Reintento %d" % tries
                try: 
                    self.socket.shutdown(SHUT_RD)
                except SocketError, e:
                    print e
                tries -= 1
                
            except Exception, e:
                print e
                return False
            else:
                return True
        return False
    
    
    def direccion(self):
        ''' Muestra la tupla IP:Puerto '''
        return (self.concentrador.ip_address, proto.TCP_PORT)
    
    def avanzar_seq_num(self):
        ''' Maneja el numero de secuencia '''
        self.seq_num += 1
        
        if self.seq_num > MAX_SEQ:
            self.seq_num = MIN_SEQ
    
    def run(self):
        ''' '''
        ConcentradorThread.queue.put(1)
        self.work()
        ConcentradorThread.queue.get()
        
    def work(self):
        ''' El hilo del concentrador '''
        print "Inciando concentrador", self.concentrador,
        print " microcontroladores 485 nros:", map(lambda c: c.id_UC, self.concentrador.uc_set.all())
        
        if not self._connect():
            print "No se pudo conectar con %s:%s" % self.direccion()
            return
        
        # Seteamos el timeout
        self.socket.settimeout(1)
        # El automata se encarga de validar la integridad de los pauqetes
        automata = UCNetPacketDetector()
        while True:
            if GLOBAL_INTERRUPT_FLAG:
                return
            if not self.concentrador.uc_set.all().count():
                print "Sin controladores que pollear"
                return
            
            data = None
            tiempo_inicial = time.time()
            
            for uc in self.concentrador.uc_set.all():
                print "Poll UC ", uc.id_UC
                p = Paquete.crear_estados_y_eventos(0x01, uc.id_UC, self.seq_num)
                print p
                try:
                    self.socket.send(p.octet_str())
                except SocketError, e:
                    print "Error en envio: %s" % e
                    return
                    
                try:
                    data = self.socket.recv(255)
                except SocketError, e:
                    print "Error en recepcion %s" % e
                else:
                    # Si recibimos datos probamos armar el paquete
                    automata.feed(data)
                
                    # Con lo que sale del automata armamos un paquete
                    r = Paquete(lista_enteros = automata.get_pkg())
                    p.evaluar_respuesta(r)
                    
                
                    print r
                    self.avanzar_seq_num()
                    
            # Calculamos el delta que tardo el poll de los micros
            delta = time.time() - tiempo_inicial
            sleep_time = self.concentrador.t_poll / 1000
            t_diff = sleep_time - delta
            if t_diff > 0:
                time.sleep(t_diff)
            else:
                print "El loop tardó %f" % delta
                print "Tiempo original esprado %f" % t_diff
                
        
def scada_main_cli(options, django_settings_module):
    '''
    Punto de entrada al scada en modo consola (CLI)
    @param options: Configuracion del motor
    @param django_settings_module: Modulo django
    '''
    setup_environ(django_settings_module)
    from dscada.apps.scada.models import Concentrador #, UC, Puerto
    
#    xh_interfase = XMLRPCThread(options.xh_iface, options.xh_port)
#    xh_interfase.start()|
    hilos_concetradores = []
    
    for con in Concentrador.objects.all():
        # Los hilos arrancan en el constructor
        hilos_concetradores.append(ConcentradorThread(con))
        
    while True:
        try:
            time.sleep(0.1)
            # Si no hay mas hilos, terminamos la aplicacion
            if ConcentradorThread.queue.empty():
                break
            
        except KeyboardInterrupt, e:
            request_shutdown()
    print "Fin del scada"