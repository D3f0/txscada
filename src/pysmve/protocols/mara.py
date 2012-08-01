# encoding: utf-8
from twisted.internet import protocol, reactor
from logging import getLogger
from constructs import MaraFrame, Event, build_mara_frame
from construct import Container

# Definiciones para mara 14 v7

logger = getLogger(__name__)

class MaraClientProtocol(protocol.Protocol):
    
    def connectionMade(self):
        logger.debug("Conection made %s" % self.endpoint)
        
    
class MaraClientProtocolFactory(protocol.Factory):
    '''
    Cliente de consultas a las placas de desarrollo
    o a un emulador'''
    pass


class MaraServer(protocol.Protocol):
    '''
    Emula el COMaster
    '''
    def __init__(self, factory):
        """Crea un protocolo que emula a un COMaster"""
        self.facotry = factory # Referencia al factory
        self._seq = 0x0
        self.current_package = None
        
    def connectionMade(self, arg):
        """docstring for connectionMade"""
        logger.debug("Servidor conectado")
        pkg_data = Container(source=0, dest=1, 
                             sequence=self.next_sequence_number(), command=0x10)
        self.transport.write(build_mara_frame(pkg_data))
        reactor.callLater(self.factory.comaster.timeout, self.timeout)
    
    
    def timeout(self):
        pass
    
    def dataReceived(self, data):
        """Recepción de datos"""
        pass
    

    def next_sequence_number(self):
        self._seq = 0x80 if self.seq == 0x0 else 0x0
        return self._seq

        
    
    
class MaraServerFactory(protocol.Protocol):
    protocol = MaraServer

    def __init__(self, comaster):
        '''CMaster'''
        self.comaster = comaster
        
    def makeConnection(self, transport):
        print "Make connection"
        return protocol.Protocol.makeConnection(self, transport)
    
    def buildProtocol(self, addr):
        #logger.debug("Creando protocolo para %s" % addr)
        print "Making connection"
        instance = self.protocol(self)
        return instance
    
    


        