# coding: utf-8

from unittest import TestCase
from ..structs import MaraFrame, TCD, any2buffer
from construct import Container
from ...constants import SOF


class ConstructTestCase(TestCase):

    def test_basic_frame_from_excel(self):

        buffer = 'FE    08    01    40    80    10    80    A7'
        contents = MaraFrame.parse(any2buffer(buffer))
        self.assertEqual(contents.sof, SOF)
        self.assertEqual(contents.source, 64)
        self.assertEqual(contents.dest, 1)
        self.assertEqual(contents.command, 0x10)
        self.assertEqual(contents.payload_10, None)
        self.assertEqual(contents.length, 8)
        self.assertEqual(contents.sequence, 128)

    def test_tcd(self):
        r = TCD.build(Container(evtype="ENERGY", q=1, addr485=1))
        s = TCD.parse(r)
        self.assertEqual(s.evtype, "ENERGY")
        self.assertEqual(s.q, 1)
        self.assertEqual(s.addr485, 1)
