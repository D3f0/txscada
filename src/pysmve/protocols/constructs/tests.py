
import sys
from datetime import datetime
from unittest import TestCase
from structs import MaraFrame, TCD, any2buffer, Event, dtime2dict
from adapters import SubSecondAdapter
from construct import Container, ULInt16
from ..constants import SOF

def _debug(v):
    sys.stderr.write("%s\n" % v)


class ConstructTestCase(TestCase):

    def test_basic_frame_from_excel(self):

        buffer = 'FE    08    01    40    80    10    80    A7'
        builded = MaraFrame.parse(any2buffer(buffer))
        self.assertEqual(builded.sof, SOF)
        self.assertEqual(builded.source, 64)
        self.assertEqual(builded.dest, 1)
        self.assertEqual(builded.command, 0x10)
        self.assertEqual(builded.payload_10, None)
        self.assertEqual(builded.length, 8)
        self.assertEqual(builded.sequence, 128)
        
        
    def test_tcd(self):
        r = TCD.build(Container(evtype="ENERGY", q=1, addr485=1))
        s = TCD.parse(r)
        self.assertEqual(s.evtype, "ENERGY")
        self.assertEqual(s.q, 1)
        self.assertEqual(s.addr485, 1)

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
        self.assertEqual(s.evtype,  'DIGITAL')
        self.assertEqual(s.port, 3)
        self.assertEqual(s.bit,  0)
        self.assertEqual(s.status,  0)


    def test_build_event_with_datetime(self):
            pass
        
    def test_energy_event(self):
        energy_data = Container(evtype="ENERGY", q=0, 
                                addr485=4,
                                idle=0, 
                                channel=0,
                                value=Container(val=0x33, q=1),
                                **dtime2dict())
        r = Event.build(energy_data)
        s = Event.parse(r)
        self.assertEqual(s.value.val,  0x33)
        self.assertEqual(s.value.q,  0x1)
        self.assertEqual(s.channel,  0)
        #_debug(pkg)


class _AdaterTestCase(TestCase):

    def test_mara_time_encapsulation(self):
        v = SubSecondAdapter(ULInt16('value')).parse('\x65\x00')
        self.assertAlmostEquals(v, 0.003, places=3)
        v = SubSecondAdapter(ULInt16('value')).parse('\xff\xfe')
        _debug(v)


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
                             payload_10=None,
                             ))
        print " ".join([("%.2x" % ord(x)).upper() for x in frame])






class SampledDataTestCase(TestCase):
    FRAMES = [
        """
            FE 44 40 01 4A 10 19 00 00 90 1D 01 00 00 00 00 00 80 80 00 00 80 80 00 00 80 80 00
            00 80 80 0F 00 00 43 00 00 00 00 04 00 04 00 04 00 04 13 48 05 51 00 51 00 51 00 51
            00 51 00 51 00 51 00 51 00 01 E1 29
        """,


        """
            FE 44 40 01 4C 10 19 00 00 85 1D 01 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 01 0F 
            00 00 43 00 00 00 00 04 00 04 00 04 00 04 13 4C 05 51 00 51 00 51 00 51 00 51 00 51 00 51 00 51 
            00 01 DD 30
        """,

        """
            FE F8 40 01 4D 10 19 00 00 8D 1D 01 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 01 0F
            00 00 43 00 00 00 00 04 00 04 00 04 00 04 13 81 09 51 00 51 00 51 00 51 00 51 00 51 00 51 00 51
            00 B5 01 93 0C 01 01 01 08 22 00 14 01 E3 0C 01 01 01 08 22 00 14 01 05 0C 01 01 01 08 22 00 14 
            01 92 0C 01 01 01 08 22 00 18 01 E2 0C 01 01 01 08 22 00 18 01 04 0C 01 01 01 08 22 00 18 01 F1 
            0C 01 01 01 08 22 00 1C 01 93 0C 01 01 01 08 22 00 1C 01 F3 0C 01 01 01 08 22 00 1C 01 05 0C 01 
            01 01 08 22 00 1C 01 F2 0C 01 01 01 08 22 00 20 01 04 0C 01 01 01 08 22 00 20 01 F0 0C 01 01 01 
            08 22 00 24 01 92 0C 01 01 01 08 22 00 24 01 15 0C 01 01 01 08 22 00 60 01 14 0C 01 01 01 08 22 
            00 7C 01 F3 0C 01 01 01 08 23 00 00 01 15 0C 01 01 01 08 23 00 00 3C 91
        """,


        """
            FE E4 40 01 F1 10 19 00 00 86 1D 01 00 00 00 00 EF 00 03 00 00 00 04 00 00 80 80 00 00 80 80 0F
            00 00 43 00 00 00 40 F6 40 F6 00 F4 00 3A 13 7F 09 00 40 00 40 00 40 00 40 00 40 00 40 00 40 00
            40 A1 45 00 0C 08 03 0F 00 00 00 00 45 01 0C 08 03 0F 00 00 00 00 
            42 00 0C 08 03 0F 00 00 00 00
            42 01 0C 08 03 0F 00 00 00 00 
            43 00 0C 08 03 0F 00 00 00 00 
            43 01 0C 08 03 0F 00 00 00 00 
            44 00 0C 08 03 0F 00 00 00 00 
            44 01 0C 08 03 0F 00 00 00 00 
            43 00 0C 08 03 0F 0F 00 00 00 
            43 01 0C 08 03 0F 0F 00 00 00 
            44 00 0C 08 03 0F 0F 00 00 00 
            44 01 0C 08 03 0F 0F 00 00 00 
            45 00 0C 08 03 0F 0F 00 00 00 
            45 01 0C 08 03 0F 0F 00 00 00 
            42 00 0C 08 03 0F 0F 00 00 00 
            42 01 0C 08 03 0F 0F 00 00 00 
            1D C2
        """,

        """
            FE 58 40 01 20 10 19 00 00 8D 1D 01 00 00 00 00 EF 00 04 00 00 00 04 00 00 80 80 00 00 80 80 0F 00 00 
            43 00 00 00 40 F6 00 F6 40 F6 40 B6 13 83 09 00 40 00 40 00 40 00 40 00 40 00 40 24 00 1E 00 15 42 00 
            0C 08 03 0E 2D 00 06 00 42 01 0C 08 03 0E 2D 00 06 00 C7 5A
        """,

        """
            FE 58 40 01 21 10 19 00 00 8D 1D 01 00 00 00 00 EF 00 04 00 00 00 04 00 00 80 80 00 00 80 80 0F 00 00 
            43 00 00 00 40 F6 40 F6 40 F6 40 B6 13 83 09 00 40 00 40 00 40 00 40 00 40 00 40 24 00 1E 00 15 43 00 
            0C 08 03 0E 2D 00 00 00 43 01 0C 08 03 0E 2D 00 00 00 90 5A
        """,

        """
            FE 58 40 01 22 10 19 00 00 8D 1D 01 00 00 00 00 EF 00 04 00 00 00 04 00 00 80 80 00 00 80 80 0F 00 00
            43 00 00 00 40 F6 40 F6 00 F4 40 B6 13 83 09 00 40 00 40 00 40 00 40 00 40 00 40 24 00 1E 00 15 44 00
            0C 08 03 0E 2D 00 0E 00 44 01 0C 08 03 0E 2D 00 0C 00 B3 5C
        """,


        """
            FE 58 40 01 23 10 19 00 00 8D 1D 01 00 00 00 00 EF 00 04 00 00 00 04 00 00 80 80 00 00 80 80 0F 00 00
            43 00 00 00 40 F6 40 F6 00 F4 00 3E 13 83 09 00 40 00 40 00 40 00 40 00 40 00 40 00 40 1E 00 15 45 00
            0C 08 03 0E 2D 00 0F 00 45 01 0C 08 03 0E 2D 00 0F 00 AC F8
        """,

    ]

    def test_sampled_data(self):
        for n, sample in enumerate(self.FRAMES):
            MaraFrame.parse(any2buffer(sample))

