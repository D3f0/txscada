# encoding: utf-8
import logging
from time import time
from twisted.internet import protocol, reactor
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread
from twisted.internet.protocol import ClientFactory

from construct import Container
from construct.core import FieldError, Struct
from ..constructs import MaraFrame
from ..constructs import upperhexstr
from ..constructs.structs import container_to_datetime
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
            # FIXME: Hacerlos con todos los campos o con ninguno
            # if self.input.command != self.output.command:
            #    logger.warn("Command not does not match with sent command %d" % self.input.command)
            # Calcular próxima sequencia
            # FIXME: Checkear que la secuencia sea == a self.output.sequence
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
        print "Acutalizando DB"
        # print self.input
        from models import DI, AI, VarSys, Energy, Event

        payload = self.input.payload_10
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
                    # di = comaster.dis.get(port = ev.port, bit = ev.bit)
                    timestamp = datetime(
                        ev.year + 2000, ev.month, ev.day, ev.hour, ev.minute, ev.second, int(ev.subsec * 100000))
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

from django.db import transaction
class MaraClientDBUpdater(MaraClientProtocol):

    '''
    This protocols saves data from scans into the
    database using Peewee ORM. This may change
    in the future.
    '''
    @transaction.commit_manually
    def saveInDatabase(self):
        from apps.mara.models import DI, AI
        from apps.hmi.models import Formula
        try:
            payload = self.input.payload_10
            if not payload:
                print "No se detecto payload!!!"
                pprint(self.input)
                return

            di_count, ai_count, sv_count = 0, 0, 0
            t0, timestamp = time(), datetime.now()
            comaster = self.factory.comaster

            for value, di in zip(iterbits(payload.dis), comaster.dis):
                old_value = DI.objects.filter(pk=di.pk).values_list('value')[0][0]
                if old_value != value:
                    print "Cambio de valor de DI", di.tag, di.port, di.bit
                di.update_value(value, timestamp=timestamp)
                di_count += 1

            for value, ai in zip(payload.ais, comaster.ais):
                ai.update_value(value, timestamp=timestamp)
                ai_count += 1

            variable_widths = [v.width for v in comaster.svs]
            #print variable_widths, len(variable_widths)
            for value, sv in zip(worditer(payload.varsys, variable_widths), self.factory.comaster.svs):
                sv.update_value(value, timestamp=timestamp)
                sv_count += 1
            print "-"*10
            print "La cantidad de ventos es:", len(payload.event)
            print "-"*10

            for event in payload.event:
                if event.evtype == 'DIGITAL':
                    # Los eventos digitales van con una DI
                    try:
                        di = DI.objects.get(ied__rs485_address = event.addr485,
                                            port=event.port,
                                            bit=event.bit)
                        fecha = container_to_datetime(event)
                        di.events.create(
                            timestamp=container_to_datetime(event),
                            q=event.q,
                            value=event.status
                            )
                        print "Evento recibido de", di.port, di.bit
                    except DI.DoesNotExist:
                        print "Evento para una DI que no existe!!!"
                elif event.evtype == 'ENERGY':
                    try:
                        query = dict(ied__rs485_address = event.addr485, channel=event.channel)
                        ai = AI.objects.get(**query)
                        ai.energy_set.create(
                            timestamp=event.timestamp,
                            code=event.code,
                            q=event.q,
                            hnn=event.hnn,
                            )
                    except AI.DoesNotExist:
                        print "Medicion de energia no reconcible", event
                    except AI.MultipleObjectsReturned:
                        print "No se pudo identificar la DI con ", query

            print "Recalculo de las formulas"
            Formula.calculate()
            transaction.commit()

            print "Update DB: DI: %d AI: %d SV: %d in %sS" % (di_count, ai_count, sv_count,
                                                              time() - t0)
        except Exception as e:
            print e


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
