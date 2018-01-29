#! /usr/bin/env python
# -*- encoding: utf-8 -*-
from picnet.proto import Paquete

import sys
sys.path.append('..')

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.python import log

# Esto no funciona

#from twisted.python.log import PythonLoggingObserver #@UnresolvedImport
#import logging
#observer = log.PythonLoggingObserver()
#console = logging.StreamHandler()
#console.setLevel(logging.INFO)
## set a format which is simpler for console use
#formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
## tell the handler to use this format
#console.setFormatter(formatter)
## add the handler to the root logger
##logging.getLogger('').addHandler(console)
##
#observer.logger.addHandler(console)
#observer.start()


# Picnet
from picnet import proto
from picnet.checksum import check_cs_bigendian

class States(object):
    '''  Colección de estados '''
    WAIT_SOF      = 0x01
    WAIT_QTY      = 0x02
    WAIT_SRC      = 0x03
    WAIT_DST      = 0x04
    WAIT_SEC      = 0x05
    WAIT_COM      = 0x06
    WAIT_DATO     = 0x07
    WAIT_BCH      = 0x08
    WAIT_BCL      = 0x09



#===============================================================================
# PicnetProtocol
#===============================================================================
class PicnetProtocol(Protocol):
    '''
    Implementacion del protocolo. Suficientemente generica como para poder
    ser usada por el cliente, y el servidor de prueba.
    '''
        
    def connectionMade(self):
        '''
        Cuando se genera una conexión
        '''
        self.reset() # Ponemos a cero
        self.peer_name = self.transport.socket.getpeername()
        log.msg("Conexoin establecida con %s" % (self.peer_name, ))
    
    # Por ahora no necesitamos este metodo
#    def connectionLost(self, reason):
#        log.msg("Se cierra conexion con %s %s " % (self.peer_name, reason.getErrorMessage() ))
        
    def reset(self):
        ''' Pone a 0 las vars de estado '''
        self.state = States.WAIT_SOF 
        self.buffer = []    # Buffer para el paquete recibido
        self.cur_pkg_len = 0    # Almacena la longitud del paquete
    
    def packageError(self, info = ''):
        ''' Este método se llaca cada vez que hay un error en el paquete '''
        log.msg("Error en estado %s %s" % (self.state, info))
        self.state = States.WAIT_SOF
        
    def dataReceived(self, data):
        ''' Datos recibidos '''
        log.msg('Recibo stream de %d bytes' % len(data))
        self.proccessData(data)
        
    def proccessData(self, data):
        ''' Porcesar el paquete, en caso de que no se requera procesar el
        paquete, se puede cambiar el rumbo en data received'''
        for c in data:
            m = self.state_sequence[self.state]
            m(self, ord(c))
    
    def handleSof(self, d):
        if d == proto.SOF:
            self.buffer = [d, ]
            self.state = States.WAIT_QTY
        else:
            self.packageError('Esperando SOF recibi %.2x' % d)
            
    def handleQty(self, d):
        if d >= proto.MIN_QTY and d <= proto.MAX_QTY:
            self.buffer.append(d)
            self.cur_pkg_len = d
            self.state = States.WAIT_SRC
        else:
            self.packageError('Esperando QTY recibi %.2x' % d)
        
    def handleSrc(self, d):
        if d >= proto.MIN_ID and d <= proto.MAX_ID:
            self.buffer.append(d)
            self.state = States.WAIT_DST
        else:
            self.packageError('Esperando SRC recibi %.2x' % d)
            
    def handleDst(self, d):
        if d >= proto.MIN_ID and d <= proto.MAX_ID:
            self.buffer.append(d)
            self.state = States.WAIT_SEC
        else:
            self.packageError('Esperando DST recibi %.2x' % d)
            
    def handleSec(self, d):
        if d >= proto.MIN_SEQ and d <= proto.MAX_SEQ:
            self.buffer.append(d)
            self.state = States.WAIT_COM
        else:
            self.packageError('Esperando SEC recibi %.2x' % d)
        
        
    def handleCom(self, d):
        # Checkear que sea un comando válido
        if d in proto.COMANDOS.values():
            self.buffer.append(d)
            # Si nos queda espacio entre sin contar el BCL, BCF
            if self.cur_pkg_len == proto.MIN_QTY:
                self.state = States.WAIT_BCH
                #log.msg("Esperando BCH")
            else:
                self.state = States.WAIT_DATO
                #log.msg("Esperando datos")
        else:
            self.packageError('Esperando COM recibi %.2x' % d)
            
    def handleDat(self, d):
        self.buffer.append(d)
        #log.msg("Recibiendo datos")
        # Si nos queda espacio entre sin contar el BCL, BCF
        if (self.cur_pkg_len - len(self.buffer)) > 2:
            self.state = States.WAIT_DATO
        else:
            self.state = States.WAIT_BCH
            
    def handleBch(self, d):
        #log.msg("BCH")
        self.buffer.append(d)
        self.state = States.WAIT_BCL
        
    def handleBcl(self, d):
        #log.msg("BCL")
        self.buffer.append(d)
        
        pkg = Paquete( self.buffer )
        if pkg.cs_ok():
            self.packageRecieved( pkg )
        else:
            self.checksumError( pkg )
            
        
        self.state = States.WAIT_SOF
    
    def checksumError(self, pkg):
        log.err(u'Error de checksum %s' % pkg)
        
    def packageRecieved(self, pkg):
        # Sobrecargar esta funcion
        log.msg(u'Paquete recibido %s' % pkg)
        
    
    # Estados para el automoata
    state_sequence = {
        States.WAIT_SOF: handleSof, 
        States.WAIT_QTY: handleQty, 
        States.WAIT_SRC: handleSrc,
        States.WAIT_DST: handleDst,
        States.WAIT_SEC: handleSec,
        States.WAIT_COM: handleCom,
        States.WAIT_DATO:handleDat,
        States.WAIT_BCH: handleBch,
        States.WAIT_BCL: handleBcl, 
                      
    }                    
        

class PicnetProtocolFactory(Factory):
    protocol = PicnetProtocol

    def __init__(self, id = 1):
        '''
        @param id: Número de identificacion, el concentrador lleva el id = 1.
        '''
        self.id = id
        