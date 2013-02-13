from unittest import TestCase
from ..structs import MaraFrame, any2buffer
from datetime import datetime
from construct import Container


class PEHTestCase(TestCase):
    def test_peh_frame(self):
        date = datetime(2012, 10, 16, 0, 55, 13)
        r = MaraFrame.parse(any2buffer('FE 11 FF 40 22 12 0C 0A 10 00 37 0D 50 3D 02 3B 48'))
        self.assertEqual(r.peh, date)

    def test_encoding(self):
        '''Puesta en hora'''
        from datetime import datetime
        frame = MaraFrame.build(Container(
                             sof=0xFE,
                             dest=1,
                             source=0,
                             sequence=32,
                             command=0x12,
                             peh=datetime.now(),
                             ))
        parsed = MaraFrame.parse(frame)
        self.assertIn('peh', parsed)
