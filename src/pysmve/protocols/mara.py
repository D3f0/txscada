# encoding: utf-8
from twisted.internet import protocol, reactor
from logging import getLogger
from constructs import MaraFrame, Event, parse_frame
from construct import Container
from construct.core import FieldError
from constructs import MaraFrame
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from protocols.constants import MAX_SEQ, MIN_SEQ
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
import models
from datetime import datetime
from utils.bitfield import bitfield
# Definiciones para mara 14 v7

logger = getLogger(__name__)


class MaraClientProtocol(protocol.Protocol):
    
    CLIENT_STATES = set(['IDLE', 'RESPONSE_WAIT', ])
    
    save_events = True
    
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
        self.timer = LoopingCall(self.timerEvent)
        self.timer.start(interval = self.factory.comaster.timeout, now = False)
        print "OK"
        
    def connectionMade(self):
        #from IPython import embed; embed()
        logger.debug("Conection made to %s:%s" % self.transport.addr)
        reactor.callLater(0.01, self.sendCommand)
    
    def timerEvent(self):
        '''Event'''
        if self.pending == 0:
            print "Sending command to %s" % (self.factory.comaster, )
        else:
            print "Sending retry %s %d" % (self.factory.comaster, self.pending)
            
        self.sendCommand()
    
    def sendCommand(self):
        # Send command
        
        frame = MaraFrame.build(self.output)
        self.transport.write(frame)
        self.state = 'RESPONSE_WAIT'
        self.pending += 1
        
        
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
            if next >= MAX_SEQ:
                next = MIN_SEQ
            self.factory.comaster.sequence = self.output.sequence = next
            print "Seq", next
            self.pending = 0
            #from IPython import embed; embed()
            deferToThread(self.saveInDatabase, response = self.input)
            
            #print self.input
            print self.transport.addr, " ".join([("%.2x" % ord(c)).upper() for c in data])
            MaraFrame.pretty_print(self.input, show_header=False, show_bcc=False)
    
    def saveInDatabase(self, response):
        print "Acutalizando DB"
        #print self.input
        from models import DI, AI, VarSys, Energy, Event
        payload = self.input.payload_10
        comaster = self.factory.comaster
        
        # Iterar de a bit
        
        def iterbits(ints, length=16):
            for val in ints:
                bf = bitfield(val)
                for i in range(length):
                    retval =  bf[i]
                    #print retval
                    yield retval
        
        
        def iterdis():
            # Iterar ieds
            for ied in self.factory.comaster.ied_set.order_by('offset'):
                # Ordenar por puerto y por bit
                for di in DI.filter(ied = ied).order_by(('port', 'asc'), ('bit', 'asc')):
                    yield di
        def iterais():
            # Iterar ieds
            for ied in self.factory.comaster.ied_set.order_by('offset'):
                # Itera por ais
                for ai in AI.filter(ied = ied).order_by('offset'):
                    yield ai
        
        def itervarsys():
            # Iterar ieds
            for ied in self.factory.comaster.ied_set.order_by('offset'):
                for varsys in VarSys.filter(ied = ied).order_by('offset'):
                    yield varsys
        
        #=======================================================================
        # Guardando...
        #=======================================================================
        for varsys, value in zip(itervarsys(), payload.varsys):
            varsys.valor = value
            varsys.save()
                            
        for di, value in zip(iterdis(), iterbits(payload.dis)):
            di.value = value
            di.save()
        
        for ai, value in zip(iterais(), payload.ais):
            ai.value = value
            ai.save()
            
        if self.save_events:
            for ev in payload.event:
                if ev.evtype == "DIGITAL":
                    ied = self.factory.comaster.ied_set.get(addr_485_IED = ev.addr485)
                    di = DI.get(ied=ied, port=ev.port, bit=ev.bit)
                    #di = comaster.dis.get(port = ev.port, bit = ev.bit)
                    timestamp = datetime(ev.year+2000, ev.month, ev.day, ev.hour, ev.minute, ev.second,int(ev.subsec*100000))
                    Event(di = di, 
                          timestamp = timestamp, 
                          subsec=ev.subsec, 
                          q=0, 
                          value = ev.status).save()
                    
                    
                elif ev.evtype == "ENERGY":
                    timestamp = datetime(ev.year+2000, ev.month, ev.day, ev.hour, ev.minute, ev.second)
                    ied = self.factory.comaster.ied_set.get(addr_485_IED = ev.addr485)
                    Energy(ied=ied, 
                           q=ev.value.q, 
                           timestamp=timestamp, 
                           address=ev.addr485, 
                           channel=ev.channel, 
                           value=ev.value.val,).save()
                    
            print ("Guardados %d eventos" % len(payload.event))
        
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
        #logger.warn("Connection failed: %s" % reason)
        print "Connection failed: %s" % reason
        print "Restarting"
        connector.connect()
        #reactor.stop()
        
    def clientConnectionLost(self, connector, reason):
        logger.warn("Connection lost: %s" % reason)
        print "Connection lost: %s" % reason
        print "Restarting"
        connector.connect()
        #reactor.stop()
    
    def startedConnecting(self, connector):
        logger.debug("Started connecting")


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
            print "%s in %s" % (e, map(lambda c: ("%.2x" % ord(c)).upper(), data))
        print "Paquete recibido"
    
    def connectionLost(self, reason):
        print "Conexion con %s:%s terminada" % self.transport.client
        
class MaraServerFactory(protocol.Factory):
    protocol = MaraServer
    def __init__(self, comaster, *largs, **kwargs):
        self.comaster = comaster
        logger.debug("Conexion con %s" % comaster)
        print comaster
        
    def makeConnection(self, transport):
        print "Make connection"
        return protocol.Protocol.makeConnection(self, transport)
    

    


        