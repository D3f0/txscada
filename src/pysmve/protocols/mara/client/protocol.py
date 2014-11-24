'''
Portocol implementation that dialogues with a Mara COMaster
It takes advantage of Twisted's inlineCallbacks
http://hackedbellini.org/development/writing-asynchronous-python-code-with-twisted-using-inlinecallbacks/
Features some basic reassembler if data comes paritioned.
'''
from __future__ import print_function
from twisted.internet import protocol
from twisted.internet import defer, reactor
from twisted.python.constants import Names, NamedConstant
from twisted.internet.threads import deferToThread
from twisted.protocols.policies import TimeoutMixin
from nguru.apps.mara.utils import get_setting, import_class
from protocols.constants import frame, sequence, commands
from construct import Container
import datetime
import logging
from protocols.constructs.structs import upperhexstr
from .log_adapter import COMasterLogAdapter
from buffer import MaraFrameReassembler


LOGGER_NAME = 'commands'


class MaraPorotocolFactory(protocol.ReconnectingClientFactory):

    def __init__(self, comaster, **options):
        '''
        This class should be instantiated by a Django management command but since
        we don't want it to have hard dependencies on Django code, we leave some
        attributes to be handled by
        '''
        self.comaster = comaster
        self.handlers = []
        logger = logging.getLogger(LOGGER_NAME)
        self.logger = COMasterLogAdapter(logger, {'comaster': self.comaster})
        self.attemps = 0

    def get_configured_construct(self):
        class_ = import_class(get_setting('MARA_CONSTRUCT'))
        return class_

    def get_configured_protocol(self):
        try:
            class_name = get_setting('MARA_CLIENT_PROTOCOL',
                                     'protocols.mara.client.protocol.MaraClientProtocol')
            class_ = import_class(class_name)
        except ImportError:
            class_ = MaraClientProtocol
        return class_

    def buildProtocol(self, addr):
        '''Constructs protocol based on configuration'''
        self.resetDelay()
        self.attemps = 0
        protocol_class = self.get_configured_protocol()
        instance = protocol_class()
        instance.construct = self.get_configured_construct()
        instance.factory = self
        instance.logger = self.logger  # Share the same logger (associates with comaster)
        return instance

    def connectTCP(self, reactor, override_ip=None):
        return reactor.connectTCP(
            host=override_ip or self.comaster.ip_address,
            port=self.comaster.port,
            factory=self,
            timeout=self.comaster.poll_interval,
        )

    def startedConnecting(self, connector):
        protocol.ReconnectingClientFactory.startedConnecting(self, connector)
        self.logger.info("Connecting to %s...", connector.getDestination())

    def clientConnectionFailed(self, connector, reason):
        self.attemps += 1
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        msg = unicode(reason).replace('\n', ' ')
        self.logger.warning("Connection failed: %s (# %d/%s)",
                            msg, self.attemps, self.maxRetries or 'oo')


class ConnectionLost(Exception):
    '''Used for singaling in callbacks'''
    pass


class Timeout(Exception):
    pass


class MaraClientProtocol(object, protocol.Protocol, TimeoutMixin):
    # Inherits from object the property new syntax

    class States(Names):
        STARTED = NamedConstant()
        CHECK_NEED_PEH = NamedConstant()
        SEND_PEH = NamedConstant()
        SEND_POLL = NamedConstant()
        WAITING_REPLY = NamedConstant()  # Workis with deferred incomingDefered
        USER_COMMAND = NamedConstant()
        GAVE_UP = NamedConstant()
        CONNECTION_LOST = NamedConstant()

    incomingDefered = None
    _state = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        assert new_state in self.States.iterconstants(), "Invalid state %s" % new_state
        self.logger.info("State change %s -> %s", self._state, new_state)
        self._state = new_state

    def sendCotainer(self, container):
        '''Convenience method for publishing when data is sent'''
        # TODO: Publish COMASTER, STATE, DATA
        assert isinstance(container, Container)
        data = self.construct.build(container)
        self.logger.info("%s >> %s", self.state, upperhexstr(data))
        self.transport.write(data)

    @property
    def comaster(self):
        '''Shortcut to comaster instance'''
        return self.factory.comaster

    def setUp(self):
        self.state = self.States.STARTED
        # Sequence
        s = self.comaster.sequence
        if s < sequence.MIN.value or s > sequence.MAX.value:
            s = sequence.MIN.value

        self.input_buffer = MaraFrameReassembler()

        self.output = Container(
            source=self.comaster.rs485_source,
            dest=self.comaster.rs485_destination,
            sequence=s,
            command=frame.SOF.value,
            payload_10=None,  # No payload,
            # peh=None,
        )

    @property
    def active(self):
        return self.state not in (self.States.CONNECTION_LOST, self.States.GAVE_UP)

    @defer.inlineCallbacks
    def mainLoop(self):
        while self.active:
            yield self.doPEH()
            replied = yield self.doPoll()
            if not replied:
                continue  # Still online?

            whatNext = yield self.waitForNextPollOrUserCommands()
            print(whatNext)

        self.transport.loseConnection()

    def waitForNextPollOrUserCommands(self):
        self.waitingDefered = defer.Deferred()
        reactor.callLater(self.comaster.poll_interval, self.waitingDefered.callback, None)
        return self.waitingDefered

    def connectionMade(self):
        self.setUp()
        reactor.callLater(0, self.mainLoop)

    def stop(self):
        self._running = False

    def buildPollContainer(self):
        return Container(
            source=self.comaster.rs485_source,
            dest=self.comaster.rs485_destination,
            sequence=self.comaster.sequence,
            command=commands.POLL.value,
            payload_10=None,  # No payload,
        )

    def buildPeHContainer(self, timestamp):
        container = Container(
            source=self.comaster.rs485_source,
            dest=0xFF,
            sequence=0xBB,
            command=commands.PEH.value,
            peh=timestamp
        )
        return container

    def pepreareToReceive(self):
        if self.state == self.States.CONNECTION_LOST:
            raise ConnectionLost()
        self.input_buffer.reset()
        self.state = self.States.WAITING_REPLY
        # Incoming defered will not be completed until a FULL package is received
        # or timeout occurs (returning None)
        self.incomingDefered = defer.Deferred()
        self.setTimeout(self.comaster.poll_interval)
        return self.incomingDefered

    @defer.inlineCallbacks
    def doPoll(self):
        self.state = self.States.SEND_POLL

        tries, max_tries = 0, self.comaster.max_retry_before_offline

        while tries <= max_tries:

            try:
                self.pepreareToReceive()
            except ConnectionLost:
                self.setTimeout(None)
                defer.returnValue(False)
                break

            # If it's not the first try, log it
            if tries:
                self.logger.debug("Retry: %s", tries)

            self.sendCotainer(self.buildPollContainer())
            try:
                data = yield self.incomingDefered

            except Timeout:
                tries += 1
                if tries > max_tries:
                    self.state = self.States.GAVE_UP
                    self.logger.warning("Giving up POLL response. Retry exceeded!")
                    defer.returnValue(False)
                    break
            except ConnectionLost:
                # Connection lost is set in handler since it's use is more general
                # self.state = self.States.CONNECTION_LOST
                defer.returnValue(False)
                break
            else:
                # We've got the data
                self.setTimeout(None)
                if not self.factory.handlers:
                    self.logger.warning("No handlers. Data may be lost")
                else:
                    self.logger.info("Calling frame handlers")
                    for h in self.factory.handlers:
                        h.handle_frame(data)

                defer.returnValue(True)
                break

    @defer.inlineCallbacks
    def doUserCommands(self):
        yield defer.returnValue(None)

    @defer.inlineCallbacks
    def doPEH(self):
        self.state = self.States.CHECK_NEED_PEH
        if self.comaster.needs_peh():
            self.state = self.States.SEND_PEH
            timestamp = datetime.datetime.now()
            self.sendCotainer(self.buildPeHContainer(timestamp))
            yield deferToThread(self.comaster.update_peh_timestamp, timestamp)
        yield defer.returnValue(None)

    def dataReceived(self, data):
        self.logger.info("%s << %s", self.state, upperhexstr(data))
        self.input_buffer += data
        if self.input_buffer.has_package():
            if self.incomingDefered:
                return self.incomingDefered.callback(self.input_buffer.get_package())
            else:
                package = self.input_buffer.get_package()
                self.logger.info("Unexpected package %s", upperhexstr(package))

    def timeoutConnection(self):
        if self.incomingDefered:
            self.incomingDefered.errback(Timeout())  # data = yield -> None (in callee)

    def connectionLost(self, reason):
        self.logger.warning("Connection lost in %s reason: %s", self.state, reason)
        self.state = self.States.CONNECTION_LOST
        self.setTimeout(None)
        if not self.incomingDefered.called:
            self.incomingDefered.errback(ConnectionLost())
