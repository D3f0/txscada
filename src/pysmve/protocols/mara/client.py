# encoding: utf-8
import logging
from time import time
import json
from twisted.internet import protocol, reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from twisted.internet.protocol import ClientFactory

from construct import Container
from construct.core import FieldError, Struct
from ..constructs import (MaraFrame, Event)
from protocols.constants import MAX_SEQ, MIN_SEQ
from datetime import datetime
from ..constructs import upperhexstr
from protocols.utils import format_buffer
from protocols.utils.bitfield import iterbits
from protocols.utils.words import worditer


class MaraClientProtocol(protocol.Protocol):
    '''
    Communitcation with one COMaster.
    A COMaster actas as a gateway with RS485 operational bay networks.
    '''

    CLIENT_STATES = set(['IDLE', 'RESPONSE_WAIT', ])

    save_events = True

    def __init__(self, factory):
        self.factory = factory
        self.state = 'IDLE'
        self.pending = 0
        self.timeouts = 0
        # Data to be sent to COMaster
        self.output = Container(
                                source=self.factory.comaster.rs485_source,
                                dest=self.factory.comaster.rs485_destination,
                                sequence=self.factory.comaster.sequence,
                                command=0x10,
                                payload_10=None, # No payload,
                                #peh=None,
                                )
        # Data to be received from COMaster
        self.input = Container()
        self.poll_timer = LoopingCall(self.pollTimerEvent)
        self.poll_timer.start(interval=self.factory.comaster.poll_interval, now=False)

        self.peh_timer = LoopingCall(self.pehTimerEvent)
        self.peh_timer.start(interval=self.factory.comaster.poll_interval * 0.5, now=False)

        reactor.callLater(0.1, self.pehTimerEvent)
        
        self.dataLogger = self.getDataLogger()
        self.logger = self.getLogger()

    def getDataLogger(self):
        '''Build logger where all communication will be printed'''
        comaster = self.factory.comaster
        profile_name = comaster.profile.name
        ip = comaster.ip_address.replace('.', '_')
        return logging.getLogger('datalogger.%s.%s' % (profile_name, ip))

    def getLogger(self):
        '''General logger'''
        comaster = self.factory.comaster
        profile_name = comaster.profile.name
        ip = comaster.ip_address.replace('.', '_')
        return logging.getLogger('protocol.%s.%s' % (profile_name, ip))

    def connectionMade(self):
        self.logger.debug("Conection made to %s:%s" % self.transport.addr)
        reactor.callLater(0.01, self.sendCommand) #@UndefinedVariable

    def getPEHContainer(self):
        return Container(
                         source=self.output.source,
                         dest=0xFF,
                         sequence=self.output.sequence,
                         command=0x12,
                         peh=datetime.now()
                         )

    def pehTimerEvent(self):
        '''Evento que inidica que se debe enviar la puesta en hora'''

        if self.state == 'IDLE':
            buffer = self.construct.build(self.getPEHContainer())
            self.transport.write(buffer)
            print "PEH >>", format_buffer(buffer)

    def pollTimerEvent(self):
        '''Event'''
        if self.pending == 0:
            print "Sending command to:", self.factory.comaster.ip_address, self.factory.comaster.sequence
        else:
            print "Sending retry %s %d" % (self.factory.comaster, self.pending)

        self.sendCommand()

    def sendCommand(self):
        # Send command

        frame = MaraFrame.build(self.output)
        self.transport.write(frame)
        self.state = 'RESPONSE_WAIT'
        self.pending += 1
    
    def logPackage(self, package):
        pass

    def incrementSequenceNumber(self):
        next_seq = self.input.sequence + 1
        if next_seq >= MAX_SEQ:
            next_seq = MIN_SEQ
        self.factory.comaster.sequence = self.output.sequence = next_seq
        self.logger.info("Sequence incremented to %d" % next_seq)
        return next_seq

    def dataReceived(self, data):
        self.dataLogger.debug('received: %s' % upperhexstr(data))
        if self.state == 'IDLE':
            self.logger.warning("Discarding data in IDLE state %d bytes" % len(data))
        elif self.state == 'RESPONSE_WAIT':
            try:
                self.input = MaraFrame.parse(data)
            except FieldError:
                self.logger.error("Bad package")
                return
            # FIXME: Hacerlos con todos los campos o con ninguno
            #if self.input.command != self.output.command:
            #    logger.warn("Command not does not match with sent command %d" % self.input.command)
            # Calcular próxima sequencia
            # FIXME: Checkear que la secuencia sea == a self.output.sequence
            self.logger.debug("Message OK")
            seq = self.incrementSequenceNumber()
            
            self.pending = 0
            
            deferToThread(self.saveInDatabase)

            print self.transport.addr, format_buffer(data)
            MaraFrame.pretty_print(self.input, show_header=False, show_bcc=False)
            self.state = 'IDLE'

    def saveInDatabase(self):
        print "Acutalizando DB"
        #print self.input
        from models import DI, AI, VarSys, Energy, Event
        payload = self.input.payload_10
        comaster = self.factory.comaster

        # Iterar de a bit

        def iterdis():
            # Iterar ieds
            for ied in self.factory.comaster.ied_set.order_by('offset'):
                # Ordenar por puerto y por bit
                for di in DI.filter(ied=ied).order_by(('port', 'asc'), ('bit', 'asc')):
                    yield di
        def iterais():
            # Iterar ieds
            for ied in self.factory.comaster.ied_set.order_by('offset'):
                # Itera por ais
                for ai in AI.filter(ied=ied).order_by('offset'):
                    yield ai

        def itervarsys():
            # Iterar ieds
            for ied in self.factory.comaster.ied_set.order_by('offset'):
                for varsys in VarSys.filter(ied=ied).order_by('offset'):
                    yield varsys

        #=======================================================================
        # Guardando...
        #=======================================================================
        for varsys, value in zip(itervarsys(), payload.varsys):
            varsys.value = value
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
                    ied = self.factory.comaster.ied_set.get(addr_485_IED=ev.addr485)
                    di = DI.get(ied=ied, port=ev.port, bit=ev.bit)
                    #di = comaster.dis.get(port = ev.port, bit = ev.bit)
                    timestamp = datetime(ev.year + 2000, ev.month, ev.day, ev.hour, ev.minute, ev.second, int(ev.subsec * 100000))
                    Event(di=di,
                          timestamp=timestamp,
                          subsec=ev.subsec,
                          q=0,
                          value=ev.status).save()


                elif ev.evtype == "ENERGY":
                    timestamp = datetime(ev.year + 2000, ev.month, ev.day, ev.hour, ev.minute, ev.second)
                    ied = self.factory.comaster.ied_set.get(addr_485_IED=ev.addr485)
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
        # Fix this horrible code!!!
        if value == 'IDLE':
            if self.queued:

                self.transport.write(self.construct.build(self.queued))
                self.queued = None

    __factory = None
    @property
    def factory(self):
        return self.__factory

    @factory.setter
    def factory(self, value):
        assert isinstance(value, ClientFactory)
        self.__factory = value

    __construct = None
    @property
    def construct(self):
        return self.__construct

    @construct.setter
    def construct(self, value):
        assert issubclass(value, Struct), "Se esperaba un Struct"
        self.__construct = value

class MaraClientDBUpdater(MaraClientProtocol):
    '''
    This protocols saves data from scans into the
    database using Peewee ORM. This may change
    in the future.
    '''
    def saveInDatabase(self):
        t0 = time()
        payload = self.input.payload_10
        di_count, ai_count, sv_count = 0, 0, 0
        timestamp = datetime.now()
        comaster = self.factory.comaster
        for value, di in zip(iterbits(payload.dis), comaster.dis):
            di.update_value(value, timestamp=timestamp)
            di_count += 1

        for value, ai in zip(payload.ais, comaster.ais):
            ai.update_value(value, timestamp=timestamp)
            ai_count += 1

        variable_widths = [ v['width'] for v in comaster.svs.values('width') ] 
        print variable_widths, len(variable_widths)
        for value, sv in zip(worditer(payload.varsys, variable_widths), self.factory.comaster.svs):
            sv.update_value(value, timestamp=timestamp)
            sv_count += 1

        print "Update DB: DI: %d AI: %d SV: %d in %sS" % (di_count, ai_count, sv_count,
                                                          time() - t0)



class MaraClientProtocolFactory(protocol.ClientFactory):
    '''Creates Protocol instances to interact with mara servers'''

    protocol = MaraClientProtocol

    def __init__(self, comaster, reconnect=True):
        self.comaster = comaster
        self.reconnect = reconnect
        self.logger = self.getLogger()

    def getLogger(self):
        return logging.getLogger("factory.%s" % (self.comaster.profile.name, ))

    def buildProtocol(self, *largs):
        p = self.protocol(factory=self)
        # TODO: Make this dynamic
        p.construct = MaraFrame
        return p

    def clientConnectionFailed(self, connector, reason):
        #logger.warn("Connection failed: %s" % reason)
        print "Connection failed: %s" % reason
        if self.reconnect:
            connector.connect()
            print "Restarting"
        else:
            reactor.stop()

    def clientConnectionLost(self, connector, reason):
        from twisted.internet import error
        self.logger.warn("Connection lost: %s" % reason)
        if reason.type == error.ConnectionLost:
            return
        if self.reconnect:
            print "Connection lost: %s. Restarting..." % reason
            connector.connect()
        else:
            reactor.stop()
