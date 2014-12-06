from twisted.trial import unittest
from twisted.test import proto_helpers
from .mocks import COMasterMock
import mock
from protocols.mara import client


class TestPoll(unittest.TestCase):

    def setUp(self):
        pass
        #self.comaster = COMasterMock()
        #self.factory = client.MaraPorotocolFactory(comaster=self.comaster)

    def test_poll_works_with_bougus_frames_from_lowlevel(self):
        """
        In some cases some wierd frames appear and make thins go wrong.

        This is a example:
        FE 08 0A 01 06 10 F1 E6 19 16 2D 2A 00 40 01 A4 50 00 00 00 00 00 00 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        00 00 00 00 00
        """
        bad_data = (
            'FE 08 0A 01 06 10 F1 E6 19 16 2D 2A 00 40 01 A4 50 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
        )

        comaster = COMasterMock()

        factory = client.MaraPorotocolFactory(comaster)
        proto = factory.buildProtocol(('127.0.0.1', 0))

        proto.doPEH = lambda *x: None

        transport = proto_helpers.StringTransport()
        proto.makeConnection(transport)
        #import ipdb; ipdb.set_trace()
        from twisted.internet import reactor
        reactor.callLater(0, lambda x: reactor.stop)
        return proto.doPoll()

    def _test_poll_timeout(self):
        proto = self.factory.buildProtocol(('127.0.0.1', 0))
        transport = proto_helpers.StringTransport()
        proto.sendPeHIfNeeded = lambda *x: None
        proto.makeConnection(transport)
        assert False

    def _test_poll_can_receive_chunked_data(self):
        assert False

    def _test_poll_updates_squence(self):
        assert False

    def _test_poll_calls_handler_when_package_is_received(self):
        assert False
