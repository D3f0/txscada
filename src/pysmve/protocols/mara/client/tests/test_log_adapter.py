import logging
from cStringIO import StringIO
from .mocks import COMasterMock
from ..log_adapter import COMasterLogAdapter
import unittest


class TestLogAdapter(unittest.TestCase):

    def setUp(self):
        self.stringio = StringIO()

        logger = logging.getLogger('')
        logger.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler(stream=self.stringio)
        ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(ch)
        self.comaster = COMasterMock()
        self.adapter = COMasterLogAdapter(logger, {'comaster': self.comaster})

    def get_logged_lines(self):
        text = self.stringio.getvalue()
        lines = text.split('\n')
        lines = filter(len, lines)
        return lines

    def test_comaster_ip_present_in_output(self):

        self.adapter.debug('debug message')
        self.adapter.info('info message')
        self.adapter.warning('warn message')
        self.adapter.error('error message')
        self.adapter.critical('critical message')

        logged_lies = self.get_logged_lines()

        self.assertEqual(len(logged_lies), 5)

        for line in self.get_logged_lines():
            self.assertIn(self.comaster.ip_address, line)
