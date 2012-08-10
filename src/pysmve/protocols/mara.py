# encoding: utf-8
from twisted.internet import protocol, reactor
from logging import getLogger
from constructs import MaraFrame, Event, parse_frame
from construct import Container
from construct.core import FieldError
from constructs import MaraFrame
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from protocols.constructs import Payload_10, format_frame
from protocols.constants import MAX_SEQ, MIN_SEQ
# Definiciones para mara 14 v7

logger = getLogger(__name__)


class MaraClientProtocol(protocol.Protocol):
    CLIENT_STATES = set(['IDLE', 'RESPONSE_WAIT', ])
    
    def __init__(self, factory):
        self.factory = factory
        self.state = 'IDLE'
        self.pending = 0
        self.timeouts = 0
        # Data to be sent to COMaster
        self.output = Container(
                                source = self.factory.comaster.source,
                                dest   = self.factory.comaster.dest,
                                sequence = self.factory.comaster.sequence,
                                command = 0x10,
                                payload_10 = None, # No payload
                                )
        # Data to be received from COMaster
        self.input = Container()
        print "OK"
        
    def connectionMade(self):
        #from IPython import embed; embed()
        logger.debug("Conection made to %s:%s" % self.transport.addr)
        reactor.callLater(0.01, self.sendCommand)
    
    def sendCommand(self):
        #logger.debug("Sending command")
        print "Sending COMMAND %s" % (self.pending if self.pending else '')
        # Send command
        frame = MaraFrame.build(self.output)
        self.transport.write(frame)
        self.state = 'RESPONSE_WAIT'
        self.timeout_deferred = reactor.callLater(self.factory.comaster.timeout, self.timeoutElapsed, )
        #self.poll_deferred = reactor
        
        
    def dataReceived(self, data):
        if self.state == 'IDLE':
            logger.warning("Discarding data in IDLE state %d bytes" % len(data))
        elif self.state == 'RESPONSE_WAIT':
            try:
                self.input = MaraFrame.parse(data)
            except FieldError:
                print "Error de paquete!"
                return
            if self.input.command != self.output.command:
                logger.warn("Command not does not match with sent command %d" % self.input.command)
            logger.debug("Message OK")
            # Calcular próxima sequencia
            next = self.input.sequence + 1
            if next == MAX_SEQ:
                next = MIN_SEQ
            self.factory.comaster.sequence = self.output.sequence = next 
            reactor.callLater(self.factory.comaster.poll_interval, self.sendCommand)
            self.timeout_deferred.cancel()
            self.pending = 0
            #print self.input
            format_frame(self.input)
            
    def timeoutElapsed(self):
        self.timeouts += 1
        self.pending += 1
        self.sendCommand()
    
    __state = 'IDLE'
    @property
    def state(self):
        return self.__state
    
    @state.setter
    def state(self, value):
        assert value in self.CLIENT_STATES, "Invalid state %s" % value
        self.__state = value
    
    __factory = None
    @property
    def factory(self):
        return self.__factory
    
    @factory.setter
    def factory(self, value):
        assert isinstance(value, ClientFactory)
        self.__factory = value
     
    
class MaraClientProtocolFactory(protocol.ClientFactory):
    '''
    Cliente de consultas a las placas de desarrollo
    o a un emulador'''
    
    protocol = MaraClientProtocol
    
    def __init__(self, comaster):
        self.comaster = comaster
    
    def buildProtocol(self, *largs):
        p = MaraClientProtocol(factory = self)
        return p
    
    def clientConnectionFailed(self, connector, reason):
        logger.warn("Connection failed: %s" % reason)
        #connector.connect()
        reactor.stop()
        
    def clientConnectionLost(self, connector, reason):
        logger.warn("Connection lost: %s" % reason)
        #connector.connect()
        reactor.stop()
    
    def startedConnecting(self, connector):
        logger.debug("Started connecting")


#===============================================================================
# COMaster emulation
#===============================================================================

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
    
    


        