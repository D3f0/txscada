# coding: utf-8

from unittest import TestCase
from ..structs import MaraFrame, TCD, any2buffer, Payload_10
from construct import Container
from ...constants import SOF
from copy import copy


class ConstructTestCase(TestCase):
    def setUp(self):
        self.base_payload = Container(
            canvarsys=1, varsys=[],
            candis=1, dis=[],
            canais=1, ais=[],
            canevs=1, event=[],
            )

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


    def test_build_payload_10(self):
        s = Payload_10.build(self.base_payload)
        self.assertEqual(len(s), 4, "No se pude generar el payload nulo."
            "Sin DI, AI, VarSys ni eventos")

    def test_build_payload_10_with_energy_event(self):
        payload = copy(payload)  # Make a copy
        event = Event.build(
            evtype=
        )
