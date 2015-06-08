"""
Portocol implementation that dialogues with a Mara COMaster
It takes advantage of Twisted's inlineCallbacks
http://hackedbellini.org/development/writing-asynchronous-python-code-with-twisted-using-inlinecallbacks/
Features some basic reassembler if data comes chunked.
"""
from __future__ import print_function
from twisted.internet import protocol
from twisted.internet import defer, reactor
from twisted.python.constants import Names, NamedConstant
from twisted.internet import threads
from twisted.protocols.policies import TimeoutMixin
from apps.mara.utils import get_setting, import_class
from protocols.constants import sequence, commands
from construct import Container, FieldError
import datetime
import logging
from protocols.constructs.structs import upperhexstr
from .log_adapter import COMasterLogAdapter
from buffer import MaraFrameReassembler

i2hex = lambda i: ('%.2x' % i).upper()

__all__ = ('MaraPorotocolFactory', 'MaraClientProtocol')

LOGGER_NAME = 'commands'


class MaraPorotocolFactory(protocol.ReconnectingClientFactory):

    def __init__(self, comaster):
        """
        This class should be instantiated by a Django management command but since
        we don't want it to have hard dependencies on Django code, we leave some
        attributes to be handled by
        """
        self.comaster = comaster
        # The handlers will be set by the management command that instanciates this
        # factory, and will be executed when a POLL frame is received.
        self.handlers = []
        logger = logging.getLogger(LOGGER_NAME)
        # This adapter prints the IP of the comaster with every log message
        self.logger = COMasterLogAdapter(logger, {'comaster': self.comaster})
        self.attemps = 0

    def get_configured_construct(self):
        """
        Takes from configuration the path to the ConsturctClass
        """
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
        """
        This method is called when a connection is made. A transient protocol
        that will handle *only* one session will be generated.
        :param addr: The address of the connection
        """
        self.resetDelay()
        self.attemps = 0
        protocol_class = self.get_configured_protocol()
        instance = protocol_class()
        instance.construct = self.get_configured_construct()
        instance.factory = self
        instance.logger = self.logger  # Share the same logger (associates with comaster)
        return instance

    def connectTCP(self, reactor, override_ip=None):
        """
        Connects the ClientFactory instance to a reactor.
        :param reactor: The reactor to bind to
        :param override_ip: The ip to be overriden.
        """
        return reactor.connectTCP(
            host=override_ip or self.comaster.ip_address,
            port=self.comaster.port,
            factory=self,
            timeout=self.comaster.poll_interval,
        )

    def startedConnecting(self, connector):
        """
        Twisted event handler. Logging purpouses.
        """
        protocol.ReconnectingClientFactory.startedConnecting(self, connector)
        self.logger.info("Connecting to %s...", connector.getDestination())

    def clientConnectionFailed(self, connector, reason):
        """
        Twisted event handler. Logging purpouses.
        """
        self.attemps += 1
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        msg = unicode(reason).replace('\n', ' ')
        self.logger.warning("Connection failed: %s (# %d/%s)",
                            msg, self.attemps, self.maxRetries or 'oo')


class ConnectionLost(Exception):
    """
    Used for singaling in callbacks
    """
    pass


class Timeout(Exception):
    """
    Used for errback in defereds that exepct input from the other side
    """
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
        # self.logger.info("State change %s -> %s", self._state, new_state)
        self._state = new_state

    def sendCotainer(self, container):
        """
        Convenience method for publishing when data is sent
        """
        # TODO: Publish COMASTER, STATE, DATA
        assert isinstance(container, Container)
        data = self.construct.build(container)
        self.logger.info("%s >> %s", self.state, upperhexstr(data))
        self.transport.write(data)

    @property
    def comaster(self):
        """
        Shortcut to comaster instance
        """
        return self.factory.comaster

    def setUp(self):
        """Initialization"""
        self.state = self.States.STARTED
        # Sequence
        s = self.comaster.sequence
        if s < sequence.MIN.value or s > sequence.MAX.value:
            s = sequence.MIN.value

        self.input_buffer = MaraFrameReassembler()

    @property
    def active(self):
        """Flag that checks if the main loop can be executed"""
        return self.state not in (self.States.CONNECTION_LOST, self.States.GAVE_UP)

    @defer.inlineCallbacks
    def mainLoop(self):
        """
        Main loop that executes the comunication. It tries to interleave every
        resposability the reactor has.
        """
        while self.active:
            yield self.doPEH()
            replied = yield self.doPoll()
            if not replied:
                continue  # Still online?

            whatNext = yield self.waitForNextPollOrUserCommands()

        self.transport.loseConnection()

    def waitForNextPollOrUserCommands(self):
        """
        Created a defered that will be callbacked form somewhere else indicating
        what shuold be done.
        """
        self.waitingDefered = defer.Deferred()
        reactor.callLater(self.comaster.poll_interval, self.waitingDefered.callback, None)
        return self.waitingDefered

    def connectionMade(self):
        """
        Called by twsited when the connection is made. The main loop is not implemented
        here for clarity reasons and testabilty using the reactor. Calls setup.
        """
        self.setUp()
        reactor.callLater(0, self.mainLoop)

    def buildPollContainer(self):
        """
        Creates a mara container using information of the comaster reference.
        """
        return Container(
            source=self.comaster.rs485_source,
            dest=self.comaster.rs485_destination,
            sequence=self.comaster.sequence,
            command=commands.POLL.value,
            payload_10=None,  # No payload,
        )

    def buildPeHContainer(self, timestamp):
        """
        Creates a PEH container.
        """
        container = Container(
            source=self.comaster.rs485_source,
            dest=0xFF,
            sequence=0xBB,
            command=commands.PEH.value,
            peh=timestamp
        )
        return container

    def pepreareToReceive(self):
        """
        Check if the connection is able to recieve data, if not ConnectionLost is risen.
        Created
        """
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
        """
        Sends Poll commands and waits for reply.
        It supports data to be chunked. It times out.

        :return bool: True if data could be retrieved from device, False otherwise.
        """
        self.state = self.States.SEND_POLL

        tries, max_tries = 0, self.comaster.max_retry_before_offline

        while tries <= max_tries:

            try:
                self.pepreareToReceive()
            except ConnectionLost:
                self.setTimeout(None)
                defer.returnValue(False)

            # If it's not the first try, log it
            if tries:
                self.logger.debug("Retry: %s", tries)

            self.sendCotainer(self.buildPollContainer())
            try:
                _str, package = yield self.incomingDefered
                self.setTimeout(None)
                try:
                    yield threads.deferToThread(self.packageReceived, package)
                    self.logger.info("Saved, next poll SEQ: %s",
                                     i2hex(self.comaster.sequence))
                except Exception:
                    self.logger.exception("Package may be lost por partially saved:")

                defer.returnValue(True)  # Return True so sleep is performed

            except FieldError, e:
                self.logger.warning("Construct error: %s", e)
            except Timeout:
                tries += 1
                if tries > max_tries:
                    self.state = self.States.GAVE_UP
                    self.logger.critical("Giving up POLL response. Retry exceeded!")
                    defer.returnValue(False)

            except ConnectionLost:
                # Connection lost is set in handler since it's use is more general
                # self.state = self.States.CONNECTION_LOST
                defer.returnValue(False)

    def packageReceived(self, package):
        """
        Called when a package is recevied. May be called from thread. Should not work
        as Deferred.

        :param package: Container parsed by self.construct
        :returns: True if the package is accepted. False otherwise, failures are logged.
        """
        if self.comaster.sequence != package.sequence:
            self.logger.warning("Expected sequence %s received %s",
                                i2hex(self.comaster.sequence),
                                i2hex(package.sequence))
        if package.dest != self.comaster.rs485_source:
            self.logger.warning("Wrong adddress: %s instead of %s",
                                package.dest,
                                self.comaster.rs485_source)
            return False

        if package.payload_10 is None:
            self.logger.warning("Payload missing.")
            return False

        self.comaster.process_frame(package, logger=self.logger)
        self.comaster.next_sequence(package.sequence)
        return True

    @defer.inlineCallbacks
    def doUserCommands(self):
        """
        To be implemeted
        """
        yield defer.returnValue(None)

    @defer.inlineCallbacks
    def doPEH(self):
        """
        Sends PEH if more than COMaster.peh_

        """
        self.state = self.States.CHECK_NEED_PEH
        if self.comaster.needs_peh():
            self.state = self.States.SEND_PEH
            timestamp = datetime.datetime.now()
            self.sendCotainer(self.buildPeHContainer(timestamp))
            yield threads.deferToThread(self.comaster.update_last_peh, timestamp)
        yield defer.returnValue(None)

    def dataReceived(self, data):
        """
        Called when data is available. It'll callback the Deferred that are waiting
        for input if it can reasseble a mara frame.
        """
        self.logger.info("%s << %s", self.state, upperhexstr(data))
        # Add data that could be chunked to the buffer
        self.input_buffer += data
        # If a package is ready (has SOF, QTY, ...) then it must be
        # parsed with self.construct reference.
        if self.input_buffer.has_package():
            if self.incomingDefered:
                raw_package_data = self.input_buffer.get_package()
                try:
                    parsed = self.construct.parse(raw_package_data)
                except FieldError:
                    self.incomingDefered.errback(FieldError(raw_package_data))
                else:
                    self.incomingDefered.callback((raw_package_data, parsed))
            else:
                package = self.input_buffer.get_package()
                self.logger.info("Unexpected package %s", upperhexstr(package))

    def timeoutConnection(self):
        """
        Called when connection is lost.
        Errbacks incoming data Deferreds.
        """
        if self.incomingDefered:
            self.incomingDefered.errback(Timeout())  # data = yield -> None (in callee)

    def connectionLost(self, reason):
        """
        Called when connection is lost. errbacks the incoming Deferreds.
        """
        self.logger.warning("Connection lost in %s reason: %s", self.state, reason)
        self.state = self.States.CONNECTION_LOST
        self.setTimeout(None)
        if not self.incomingDefered.called:
            self.incomingDefered.errback(ConnectionLost())
