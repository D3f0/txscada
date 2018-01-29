# -*- coding: utf-8 -*-

from django.test import TestCase
from factories import COMasterFactory, SMVETreeCOMaseterFactory
from apps.mara.models import AI


class TestQPropagation(TestCase):
    def setUp(self):
        self.co_master = COMasterFactory()


    def test_farme_sv_is_propagated_to_ai(self):
        '''
        Spanish Requirement:
        Cuando del campo viene un 0x4xxx significa calificador en 1
        (ej: con valor CERO forzado), luego la medida se debiera expresar en ROJO
        tal cual la fórmula asociada
        (hay que parsear el calificador: los dos bits más altos)'''
        pass


class TestAIQualityMethods(TestCase):
    def setUp(self):
        self.co_master_0 = SMVETreeCOMaseterFactory()
        self.co_master_1 = SMVETreeCOMaseterFactory(profile=self.co_master_0.profile)


    def test_set_ai_q_for_all_ais(self):
        '''Setting COMaster AI's q should not affect other AIs in other COMasters'''
        self.co_master_0.ais.update(q=0)
        self.co_master_1.ais.update(q=1)
        value = 1
        self.co_master_0.set_ai_qualifier(value=value)
        values = self.co_master_0.ais.values_list('q', flat=True)
        for v in values:
            self.assertEqual(v, value, "q should have been set to %s" % value)

        values = self.co_master_0.ais.values_list('q', flat=True)
        for v in values:
            self.assertEqual(v, 1, "q should not have been modified")