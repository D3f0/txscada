# coding: utf-8
'''

Se destaca en rojo el primer byte de las varsys respectivas que ponen 10 porque el
CoMAster detectó no respuesta luego de 5 mensajes din respuesta.

FE 8C 40 01 6E 10 3D 83 00 00 FC 01 46 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00
00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00
00 10 00 00 00 00 00 19 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 2D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 A6 34


Esta trama es la misma que la anterior pero tiene las medidas del primer IED Alpha
(con varsys en rojo) ver campo de medidasacusando calificador en 1. Ojo que esta trama
tiene el check sum erróneo.

FE 8C 40 01 6E 10 3D 83 00 00 FC 01 46 43 00 00 00 00 01 10 00 00 00 00 00 10 00 00 00 00
00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00
00 10 00 00 00 00 00 19 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 2D 00 00 00 00 00 00 00 00 00 48 00 4F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 A6 34


'''


TEST_FRAME_1 = '''
FE 8C 40 01 6E 10 3D 83 00 00 FC 01 46 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00
00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00
00 10 00 00 00 00 00 19 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 2D 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 A6 34'''


TEST_FRAME_2 = '''
FE 8C 40 01 6E 10 3D 83 00 00 FC 01 46 43 00 00 00 00 01 10 00 00 00 00 00 10 00 00 00 00
00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00 00 10 00 00 00 00
00 10 00 00 00 00 00 19 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 2D 00 00 00 00 00 00 00 00 00 48 00 4F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 A6 34'''


from django.test import TestCase
from factories import (ProfileFactory, COMasterFactory, IEDFactory, DIFactory, AIFactory,
                       SVGScreenFactory, SVGElementFactory, FormulaFactory)

from protocols.constructs.structs import parse_frame

class TestCalificadores(TestCase):

    def setUp(self):
        self.profile = ProfileFactory()
        self.co_master = COMasterFactory(profile=self.profile)
        self.payload_frame_1 = parse_frame(TEST_FRAME_1)
        self.payload_frame_2 = parse_frame(TEST_FRAME_2)

    def test_varsys_q_is_set_in_ais(self):
        assert False