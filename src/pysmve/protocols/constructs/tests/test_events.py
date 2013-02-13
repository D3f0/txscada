# encoding: utf-8

from construct import Container
from unittest import TestCase
from ..structs import Event
from datetime import datetime


class EventTestCase(TestCase):
    def test_digital_event(self):
        event_data = Container(evtype="DIGITAL",
                                addr485=5,
                                bit=0,
                                port=3,
                                status=0,
                                year=12,
                                month=1,
                                day=1,
                                hour=12,
                                minute=24,
                                second=10,
                                subsec=.33,
                                value=None,
                                q=0,
                                )
        r = Event.build(event_data)
        s = Event.parse(r)

        assert False

        self.assertEqual(s.evtype,  'DIGITAL')
        self.assertEqual(s.port, 3)
        self.assertEqual(s.bit,  0)
        self.assertEqual(s.status,  0)

    def test_energy_event(self):
        energy_data = Container(evtype="ENERGY", q=0,
                                addr485=4,
                                idle=0, code=0, # Energía de 15 minutos
                                channel=0,
                                value=131583,
                                datetime=datetime.now())
        r = Event.build(energy_data)
        s = Event.parse(r)
        self.assertEqual(s.value.val,  0x33)
        self.assertEqual(s.value.q,  0x1)
        self.assertEqual(s.channel,  0)

    def test_event_type_3(self):
        code = 2
        motiv = 2
        diag_data = Container(
            # 1 byte (TCD)
            evtype="DIAG", q=0, addr485=4,
            # 2 byte
            code=code, motiv=motiv,
            **dtime2dict()
        )
        r = Event.build(diag_data)
        s = Event.parse(r)
        self.assertEqual(s.code, code)
        self.assertEqual(s.motiv, motiv)

