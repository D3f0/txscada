# from twisted.trial import unittest
from nguru.apps.mara.tests.factories import SMVETreeCOMaseterFactory
from django.test import TestCase
from twisted.test import proto_helpers


class TestPoll(TestCase):

    def setUp(self):
        self.co_master = SMVETreeCOMaseterFactory()
        self.proto_factory = self.co_master.get_protocol_factory()

    def _make_protocol(self):
        proto = self.proto_factory.buildProtocol(('127.0.0.1', 0))
        tr = proto_helpers.StringTransport()
        proto.makeConnection(tr)
        return proto, tr

    def test_poll_timeout(self):
        pass

    def test_poll_can_receive_chunked_data(self):
        assert False

    def test_poll_updates_squence(self):
        # Based on
        # http://twistedmatrix.com/documents/12.3.0/core/howto/trial.html
        proto, tr = self._make_protocol()

        assert False

    def test_poll_calls_handler_when_package_is_received(self):
        assert False
