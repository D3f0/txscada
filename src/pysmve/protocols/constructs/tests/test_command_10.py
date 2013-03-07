# coding: utf-8

from unittest import TestCase
from ..structs import MaraFrame, TCD, any2buffer, Payload_10
from construct import Container
from ...constants import SOF
from copy import copy
from datetime import datetime


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


    def _build_energy_event_container(self, **kwargs):
        event = Container(
            evtype="ENERGY", q=0, addr485=1,
            idle=0, code=0, channel=0,
            value=1 << 17,
            timestamp=datetime(2012, 1, 1, 12, 30, 12)
        )
        event.update(kwargs)
        return event

    def test_build_payload_10_with_energy_event(self):
        '''Test energy energy to a payload with events'''
        event_size = 10  # Bytes
        payload = copy(self.base_payload)  # Make a copy
        event = self._build_energy_event_container()
        # Update event count
        payload.event.append(event)
        payload.canevs = event_size + 1
        # Build payload
        s = Payload_10.build(payload)
        self.assertGreater(len(s), 8)
        # Back to container
        r = Payload_10.parse(s)
        self.assertEqual(len(r.event), 1)
        # Test if all values are the same
        for key, value in event.iteritems():

            self.assertEqual(value, event[key], "Payload should not be mangled in "
                                                    "construct")
