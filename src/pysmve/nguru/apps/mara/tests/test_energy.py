# -*- coding: utf-8 -*-

from unittest import TestCase
from protocols.constructs.structs import MaraFrame
from apps.mara.tests.factories import (ProfileFactory, COMasterFactory, IEDFactory,
                                       AIFactory)


class EnergyTestCase(TestCase):
    def setUp(self):
        self.profile = ProfileFactory()
        self.co_master = COMasterFactory(profile=self.profile)
        self.ied = IEDFactory(co_master=self.co_master)
        self.ai0 = AIFactory(ied=self.ied)
        self.ai1 = AIFactory(ied=self.ied)
        self.ai2 = AIFactory(ied=self.ied)

    def test_energy_for_23_59(self):
        '''
        Cálculo de los pulsos de Energía de la hora 23:59 (CODE 3)
        Hay errror en la forma que se totaliza. Los bytes del cálculo son TRES.
        Ocupan la 8va,9na y10ma (ultimas tres) posición en la trama del evento.
        Debe utilizarse una variable LongInt (32 bits). El cálculo es:
        8va*65536 + 10ma*256 + 9na. (tomar los bytes como NO signados).
        '''

        assert False