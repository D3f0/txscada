# encoding: utf-8

from twisted.internet import protocol, reactor
from logging import getLogger
from construct import Container
from construct.core import FieldError, Struct
from twisted.internet.protocol import ClientFactory
from ..constructs import (MaraFrame, Event)
from protocols.constants import MAX_SEQ, MIN_SEQ
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from datetime import datetime
from ..utils.bitfield import bitfield
from ..constructs import upperhexstr
import models

logger = getLogger(__name__)

#===============================================================================
# COMaster emulation
#===============================================================================

class MaraServer(protocol.Protocol):
    '''
    Works as COMaster development board
    It replies commands 0x10 based on the definition 
    in the comaster instance (a DB table).
    '''
    comaster = None
    def __init__(self):
        """Crea un protocolo que emula a un COMaster"""
        self.input = None
        self.output = None
        
        
    def connectionMade(self,):
        """docstring for connectionMade"""
        #from ipdb import set_trace; set_trace()
        logger.debug("Conection made to %s:%s" % self.transport.client)
    
    def dataReceived(self, data):
        """Recepción de datos"""
        try:
            self.input = MaraFrame.parse(data)
        except FieldError as e:
            # If the server has no data, it does not matter
            logger.warn("Error de pareso: %s" % upperhexstr(data))
        self.maraPackageReceived()
    
    def maraPackageReceived(self):
        pass
        """Note: Input holds input package parse results"""
        if self.input.command == 0x10:
            # Response for command 0x10
            self.transport.write(self.makeResponse10)
    
    def makeResponse10(self):
        pass
    
    def connectionLost(self, reason):
        print "Conexion con %s:%s terminada" % self.transport.client

class MaraServerSimulator(MaraServer):
    pass

class MaraServerFactory(protocol.Factory):
    protocol = MaraServer
    def __init__(self, comaster, *largs, **kwargs):
        self.comaster = comaster
        logger.debug("Conexion con %s" % comaster)
        print comaster
        
    #def makeConnection(self, transport):
    #    print "Make connection"
    #    return protocol.Protocol.makeConnection(self, transport)
    

    


        