from django_fasttest import TestCase
from factories import (ProfileFactory, COMasterFactory, IEDFactory, DIFactory, AIFactory,
                       SVGScreenFactory, SVGElementFactory, FormulaFactory)
from protocols.constructs.structs import hexstr2buffer
from protocols.constructs import MaraFrame

FRAME = 'FE FC 40 01 5F 10 43 20 00 00 78 01 01 44 0E 01 00 94 02 44 0D 05 00 1C 02 44 23 04 00 09 02 44 15 03 00 72 02 44 03 02 00 29 02 43 05 05 00 00 01 41 0B 00 00 B5 86 41 0D FF FF 4C 48 43 11 02 00 00 01 10 00 00 00 00 00 1B 11 00 14 55 00 00 04 26 00 26 04 06 00 06 00 06 00 26 04 06 00 06 04 06 00 00 31 D9 0B 00 00 CB 0B D2 0D 60 01 AB 00 3D 03 32 01 00 40 00 40 00 40 00 40 6B 02 F8 00 BF 00 49 00 00 40 00 40 00 40 00 40 00 40 00 40 00 00 00 00 65 42 18 0E 01 14 17 3B 1D 76 6C 42 19 0E 01 14 17 3B 11 A5 CB 43 08 0E 01 14 17 3B 00 CF 05 43 09 0E 01 14 17 3B 00 1E 02 44 18 0E 01 14 17 3B 00 00 00 44 19 0E 01 14 17 3B 00 00 00 45 08 0E 01 14 17 3B 00 00 00 45 09 0E 01 14 17 3B 00 00 00 46 18 0E 01 14 17 3B 37 0E 74 46 19 0E 01 14 17 3B 1A 1E 24 A9 3B'

class TestEnergy2359(TestCase):
    def setUp(self):
        buffer = hexstr2buffer(FRAME)
        payload = MaraFrame.parse(buffer).palyload_10
        ied = IEDFactory()

    def test_is_parsed_correctly(self):
        assert False