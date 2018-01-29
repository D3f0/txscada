# -*- coding: utf-8 -*-
import datetime
from twisted.internet.protocol import ClientFactory
from twisted.test import proto_helpers
from twisted.internet import reactor
from mock import MagicMock, patch, Mock
from protocols.constructs import MaraFrame
from twisted.trial import unittest
from .mocks import COMasterMock
from protocols.mara.client import MaraClientProtocol, MaraPorotocolFactory


class BaseTestProtocol(unittest.TestCase):

    def setUp(self):
        self.comaster = COMasterMock()


class TestProtocolPeh(BaseTestProtocol):

    def test_send_peh_upon_connection(self):
        '''To test client protocol we isloate it from the ClientFactory'''
        with patch.object(datetime, 'datetime', Mock(wraps=datetime.datetime)) as patched:
            fixed_date = datetime.datetime(2014, 1, 1, 12, 0, 0)
            patched.now.return_value = fixed_date

            factory = ClientFactory()
            factory.comaster = self.comaster

            factory.protocol = MaraClientProtocol
            proto = factory.buildProtocol(('127.0.0.1', 0))
            proto.construct = MaraFrame

            # Disable unnesesary behaviour
            def stop():
                proto.stop()
                reactor.stop()
            proto.sendPoll = MagicMock(side_effect=stop)

            transport = proto_helpers.StringTransport()
            proto.makeConnection(transport)

            bytes_sent_to_device = transport.value()
            result = MaraFrame.parse(bytes_sent_to_device)
            self.assertEqual(result.dest, 0xFF)
            self.assertEqual(result.source, 2)

            # We don't need to check BCC since it's already coded into MaraFrame
            self.assertEqual(result.peh, fixed_date)

            reactor.run()
            # Shuld have stopped
            self.assertEqual(self.comaster.update_peh_timestamp.call_count, 1)
            self.assertEqual(self.comaster.update_peh_timestamp.call_args[0][0],
                             fixed_date)


class TestPrtocolFactory(unittest.TestCase):
    def setUp(self):
        self.comaster = COMasterMock()
        self.factory = MaraPorotocolFactory(self.comaster)

    def test_protocol_holds_reference_to_factory(self):
        protocol = self.factory.buildProtocol(('127.0.0.1', 0))
        self.assertEqual(protocol.factory, self.factory)

    def test_protocol_holds_reference_to_comaster(self):
        protocol = self.factory.buildProtocol(('127.0.0.1', 0))
        self.assertEqual(protocol.comaster, self.comaster)
