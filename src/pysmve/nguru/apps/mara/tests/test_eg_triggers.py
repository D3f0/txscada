# encoding: utf-8

from django_fasttest import TestCase
from apps.mara.models import DI
from apps.hmi.models import SVGElement

from nguru.apps.mara.tests.factories import IEDFactory, ProfileFactory, COMasterFactory


class DigitalEventUpdatesSVGElementTextTest(TestCase):
    def setUp(self):
        self.profile = ProfileFactory()
        self.comaster = COMasterFactory(profile=self.profile)
        self.ied = IEDFactory(co_master=self.comaster)
        description = 'Test DI'
        self.di = self.ied.di_set.create(port=0, bit=0, description=description)


    def test_di_events_are_propagated(self):
        assert False