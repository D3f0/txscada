# encoding: utf-8

from construct import Container
from unittest import TestCase
from ..structs import MaraFrame, Event, container_to_datetime
from datetime import datetime


MARA_RESOLUTION = (float(1024) / 32768) * 1000000


class DateTimeComparisionTestCase(TestCase):
    def assertAlmostEqual(self, first, second, delta=MARA_RESOLUTION, **kwargs):
        '''Compraision datetime aware'''
        if isinstance(first, datetime) and isinstance(second, datetime):
            all_but_micro = lambda d: (d.year, d.month, d.day, d.hour, d.minute, d.second)
            self.assertEqual(all_but_micro(first), all_but_micro(second),
                ("%s and %s are not have the same year, month, day, hour, minute or "
                    "second data") %
                    (first, second))
            super(DateTimeComparisionTestCase, self).assertAlmostEqual(first.microsecond,
                second.microsecond, delta=delta,
                msg="%s and %s differ in microseconds" % (first, second)
                )
        else:
            super(DateTimeComparisionTestCase, self).assertAlmostEqual(first, second,
                delta=delta, **kwargs)


class EventTestCase(DateTimeComparisionTestCase):
    event_data = Container(evtype="DIGITAL", q=0,
                               addr485=5, bit=0, port=3, status=0,
                               # Timestamp bytes
                               timestamp=datetime.now()
                               )
    def test_digital_event_dont_lose_time_data(self):
        '''Event can be created from bytes'''

        r = Event.build(self.event_data)
        s = Event.parse(r)

        self.assertIn('year', s)
        self.assertIn('month', s)
        self.assertIn('day', s)
        self.assertIn('hour', s)
        self.assertIn('minute', s)
        self.assertIn('second', s)
        self.assertIn('fraction', s)

    def test_digital_event_using_adapter(self):
        '''But it's easier to use the adapter'''
        timestamp = datetime.now()
        event_data = Container(evtype="DIGITAL", addr485=5, bit=0, port=0, status=0, q=0,
                               timestamp=timestamp,

                               )
        build = Event.build(event_data)
        parsed = Event.parse(build)

        self.assertAlmostEqual(container_to_datetime(parsed), timestamp)

    def test_energy_event(self):
        energy_data = Container(evtype="ENERGY", q=0,
                                addr485=4,
                                idle=0, code=0,  # Energía de 15 minutos
                                channel=0,
                                value=131583,
                                timestamp=datetime.now())
        r = Event.build(energy_data)
        s = Event.parse(r)

    def test_comsys_event(self):
        '''Eventos de tipo 3'''

        code = 2
        motiv = 2
        diag_data = Container(
            # 1 byte (TCD)
            evtype="COMSYS", q=0, addr485=4,
            # 2 byte
            code=code, motiv=motiv,
            timestamp=datetime(2012, 1, 1, 1, 1, 1, 50000)
        )

        r = Event.build(diag_data)
        s = Event.parse(r)
        self.assertEqual(s.code, code)
        self.assertEqual(s.motiv, motiv)

    def test_energy_event(self):
        ev = Container()
        ev.evtype = "ENERGY"
        ev.addr485 = 0
        ev.idle = 0
        ev.code = 1
        ev.channel = 0
        ev.timestamp = datetime.now()
        ev.value = 1 << 16
        ev.hnn=0
        ev.q = 0
        stream = Event.build(ev)
        result = Event.parse(stream)
        def dec(vs):
            output = 0
            for i, v in enumerate(vs):
                output += v << (i * 8)
            return output
        self.assertEqual(dec(result.data), ev.value)



    def test_command_10_with_events(self):
        # Cut and paste from parsed

        # digital_event = {'status': 0, 'addr485': 1, 'hour': 1, 'year': 12, 'month': 1,
        # 'q': 0, 'second': 34, 'minute': 8, 'fraction': 124, 'evtype': 'DIGITAL',
        # 'bit': 4, 'port': 1, 'day': 1}

        data = Container(
            sof=0xFE,
            length=0,
            dest=1,
            source=2,
            sequence=0x33,
            command=0x10,
            payload_10=Container(
                    canvarsys=2,
                    varsys=[33],
                    candis=0,
                    dis=[],
                    canais=0,
                    ais=[],
                    canevs=11,
                    event=[self.event_data, ]
                )
            )
        stream = MaraFrame.build(data)

        import sys
        sys.stdout.write(stream)

