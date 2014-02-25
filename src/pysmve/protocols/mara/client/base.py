# encoding: utf-8
import logging
from time import time
from twisted.internet import protocol, reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from twisted.internet.protocol import ClientFactory

from construct import Container
from construct.core import FieldError, Struct
from ...constructs import (MaraFrame,
                           upperhexstr)
from ...constructs.structs import container_to_datetime
from protocols.constants import MAX_SEQ, MIN_SEQ
from datetime import datetime
from protocols.utils import format_buffer
from protocols.utils.bitfield import iterbits
from protocols.utils.words import worditer
from pprint import pprint


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
        seq = self.factory.comaster.sequence
        if seq < MIN_SEQ or seq > MAX_SEQ:
            seq = MIN_SEQ
        # Data to be sent to COMaster
        self.output = Container(
            source=64,
            dest=1,
            sequence=seq,
            command=0x10,
            payload_10=None,  # No payload,
            # peh=None,
        )
        # Data to be received from COMaster
        self.input = Container()
        self.poll_timer = LoopingCall(self.pollTimerEvent)
        self.poll_timer.start(interval=self.factory.comaster.poll_interval, now=False)

        self.setupPEH()

        self.dataLogger = self.getDataLogger()
        self.logger = self.getLogger()

    def setupPEH(self, initial_delay=0.1):
        # Puesta en hora
        self.peh_timer = LoopingCall(self.pehTimerEvent)
        interval = self.factory.comaster.peh_time
        interval = interval.hour * 60 * 60 + interval.minute * 60 + interval.second
        self.peh_timer.start(interval=interval, now=False)
        # Puesta en hora inmediata
        reactor.callLater(initial_delay, self.pehTimerEvent)

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
        reactor.callLater(0.01, self.sendCommand)  # @UndefinedVariable

    def getPEHContainer(self):
        return Container(
            source=self.output.source,
            dest=0xFF,
            sequence=0xBB,
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
        self.dataLogger.debug('Sent: %s' % upperhexstr(frame))
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
        self.factory.comaster.save()
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

            # Command 17
            if self.input.command != self.output.command:
                self.logger.warn("Command not does not match with sent command %d" % self.input.command)
                self.state = 'IDLE'
                return

            # Calcular próxima sequencia
            # FIXME: Checkear que la secuencia sea == a self.output.sequence
            if self.input.length < 0xA:
                self.logger.error("Paquete de largo insuficiente")
                return
            if self.input.sequence != self.output.sequence:
                self.logger.error("Paquete secuencia diferente")
                return

            self.logger.debug("Message OK")
            #self.incrementSequenceNumber()
            self.output.sequence += 1
            if self.output.sequence > 127:
                self.output.sequence = 32
            self.factory.comaster.sequence = self.output.sequence
            self.factory.comaster.save()

            self.pending = 0

            if self.factory.defer_db_save:
                deferToThread(self.saveInDatabase)
            else:
                self.saveInDatabase()

            #MaraFrame.pretty_print(self.input, show_header=False, show_bcc=False)
            self.state = 'IDLE'

    def saveInDatabase(self):
        raise NotImplementedError("You should override this class")

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




class MaraClientProtocolFactory(protocol.ClientFactory):

    '''Creates Protocol instances to interact with mara servers'''

    protocol = MaraClientProtocol
    defer_db_save = False

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
        # logger.warn("Connection failed: %s" % reason)
        print "Connection failed: %s" % reason
        if self.reconnect:
            reactor.callLater(5, self.restart_connector, connector=connector)
        else:
            reactor.stop()

    def clientConnectionLost(self, connector, reason):
        from twisted.internet import error
        self.logger.warn("Connection lost: %s" % reason)
        print "Connection lost: %s. Restarting..." % reason
        # if reason.type == error.ConnectionLost:
        #     return
        if self.reconnect:
            print "Recconnection in 5"
            reactor.callLater(5, self.restart_connector, connector=connector)
        else:
            reactor.stop()

    def restart_connector(self, connector):
        print "Reconnecting"
        try:

            connector.connect()
        except Exception as e:
            print e
