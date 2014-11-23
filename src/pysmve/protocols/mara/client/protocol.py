'''
Portocol implementation that dialogues with a Mara COMaster
It takes advantage of Twisted's inlineCallbacks
http://hackedbellini.org/development/writing-asynchronous-python-code-with-twisted-using-inlinecallbacks/
Features some basic reassembler if data comes paritioned.
'''
from __future__ import print_function
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import defer, protocol
from twisted.python.constants import Names, NamedConstant
from twisted.internet.threads import deferToThread
from twisted.protocols.policies import TimeoutMixin
from nguru.apps.mara.utils import get_setting, import_class
from protocols.constants import frame, sequence
from construct import Container
import datetime


class MaraPorotocolFactory(ReconnectingClientFactory):

    def get_configured_construct(self):
        construct_class = import_class(get_setting('MARA_CONSTRUCT'))
        return construct_class

    def get_configured_protocol(self):
        class_name = get_setting('MARA_CLIENT_PROTOCOL',
                                 'protocols.mara.client.protocol.MaraClientProtocol')
        construct_class = import_class(class_name)
        return construct_class

    def __init__(self, co_master, settings, auto_connect=True):
        self.co_master = co_master
        self.settings = settings
        self.retrys = 0

    def buildProtocol(self):
        '''Constructs protocol based on configuration'''
        protocol = self.get_configured_protocol()
        protocol.construct = self.get_configured_construct()
        return protocol


class MaraClientProtocol(Protocol, TimeoutMixin):
    defered = None
    _state = None

    class States(Names):
        STARTED = NamedConstant()
        SEND_PEH = NamedConstant()
        POLLING = NamedConstant()
        USER_COMMAND = NamedConstant()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        assert new_state in self.States.iterconstants(), "Invalid state %s" % new_state
        print(self.state, "->", new_state)
        self._state = new_state

    @property
    def comaster(self):
        '''Shortcut to comaster instance'''
        return self.factory.comaster

    def send(self, data):
        '''Convenience method for publishing when data is sent'''
        # TODO: Publish COMASTER, STATE, DATA
        if isinstance(data, Container):
            to_send = self.construct.build(data)
        else:
            to_send = data
        print("Sending", self.state, data)
        self.transport.write(to_send)

    def setUp(self):
        self.state = self.States.STARTED
        s = self.comaster.sequence
        if s < sequence.MIN.value or s > sequence.MAX.value:
            s = sequence.MIN.value

        self.output = Container(
            source=self.comaster.rs485_source,
            dest=self.comaster.rs485_destination,
            sequence=s,
            command=frame.SOF.value,
            payload_10=None,  # No payload,
            # peh=None,
        )

    _running = True

    @defer.inlineCallbacks
    def connectionMade(self):
        self.setUp()

        while self._running:
            yield self.sendPeHIfNeeded()
            yield self.sendPoll()
            yield self.sendUserCommands()

        self.transport.loseConnection()

    def stop(self):
        self._running = False

    def waitForData(self):
        self.defered = defer.Deferred()
        return self.defered

    @defer.inlineCallbacks
    def sendPoll(self):
        tries = 0
        while tries < 3:
            self.send('request')
            self.setTimeout(self.comaster.poll_interval)
            data = yield self.waitForData()
            if not data:
                tries += 1
                continue
            print("connectionMade data received :D", data)
            defer.returnValue(None)
        raise Exception('MaxRetry')

    @defer.inlineCallbacks
    def sendUserCommands(self):
        yield defer.returnValue(None)

    def buildPeHContainer(self, timestamp):
        container = Container(
            source=self.output.source,
            dest=0xFF,
            sequence=0xBB,
            command=0x12,
            peh=timestamp
        )
        return container

    @defer.inlineCallbacks
    def sendPeHIfNeeded(self):
        self.state = self.States.SEND_PEH
        timestamp = datetime.datetime.now()
        payload = self.buildPeHContainer(timestamp)
        self.send(payload)
        yield deferToThread(self.comaster.update_peh_timestamp, timestamp)
        yield defer.returnValue(None)

    def dataReceived(self, data):
        # print("Received", data)
        if self.defered:
            self.defered.callback(data)
        else:
            print("Unexpected data", data)

    def timeoutConnection(self):
        if self.defered:
            self.defered.callback(None)
