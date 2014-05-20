import factory
from factory.django import DjangoModelFactory as ORMFactory
from django.contrib.contenttypes.models import ContentType
from apps.mara.models import (Profile, COMaster, IED, AI, DI, SV
                              #, Energy, Event, ComEvent)
                              )

import logging
logging.getLogger("factory").setLevel(logging.WARN)

from django.contrib.auth.models import User


class UserFactory(ORMFactory):
    FACTORY_FOR = User

from apps.hmi.models import (SVGElement, SVGScreen, Formula, SVGPropertyChangeSet, Color)


class ContentTypeSequencer(object):
    def __init__(self):
        self.sequences = {}

    def __call__(self, instance, start=0):
        ct_pk = ContentType.objects.get_for_model(instance).pk
        key = (ct_pk, instance.pk)
        if not key in self.sequences:
            self.sequences[key] = start
        else:
            self.sequences[key] += 1

        return self.sequences[key]

insance_sequence = ContentTypeSequencer()


class ProfileFactory(ORMFactory):
    FACTORY_FOR = Profile


class COMasterFactory(ORMFactory):
    FACTORY_FOR = COMaster
    profile = factory.SubFactory(ProfileFactory, name='default')
    ip_address = factory.Sequence(lambda n: '192.168.1.%d' % (n + 1))
    enabled = True
    description = factory.LazyAttribute(lambda s: 'Description for %s' % s.ip_address)



def SMVETreeCOMaseterFactory(can_ieds=3, can_dis=48, *args, **kwargs):
    '''
    Created a COMaster that mimics hardware configuration.
    SV are always 6.
    DI are all tied to first IED (COMaster acting as IED)
    AI are 4 to the first IED (with channel=0) and then 2 for each IED.
    This configuraion is specific to SMVE.
    '''

    co_master = COMasterFactory(*args, **kwargs)

    for n_ied in range(can_ieds):
        ied = IEDFactory(co_master=co_master, rs485_address=n_ied+1)

        if n_ied == 0:
            # Only first IED has DIs
            for n_di in range(can_dis):
                port = n_di / 16
                bit = n_di % 16
                DIFactory(ied=ied, port=port, bit=bit)
            # Create 4 AIs for first IED (voltage)
            for i in range(4):
                AIFactory(ied=ied, channel=0)
        else:
            # AIs
            AIFactory(ied=ied, channel=0)
            AIFactory(ied=ied, channel=1)


        SVFactory(ied=ied, param='ComErrorL', description='MOTIV -CoMaster')
        SVFactory(ied=ied, param='ComErrorH', description='No Implementado')
        SVFactory(ied=ied, param='Sesgo', description='L Sesgo (Entero)')
        SVFactory(ied=ied, param='Sesgo', description='H Sesgo (Entero)')
        SVFactory(ied=ied, param='CalifL', description='GaP del clock')
        SVFactory(ied=ied, param='CalifH', description='Error-Arranque UART')

    return co_master

class IEDFactory(ORMFactory):
    FACTORY_FOR = IED
    co_master = factory.SubFactory(COMasterFactory)
    rs485_address = factory.Sequence(lambda n: n+1)
    #offset = factory.LazyAttribute(lambda s: insance_sequence(s.co_master))

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        """Ensure sequential offset for every IED related to a COMaster"""
        if not 'offset' in kwargs and 'co_master' in kwargs:
            co_master = kwargs['co_master']
            kwargs['offset'] = co_master.ieds.count()
        return kwargs


class AIFactory(ORMFactory):
    FACTORY_FOR = AI
    ied = factory.SubFactory(IEDFactory)
    offset = factory.LazyAttribute(lambda s: insance_sequence(s.ied))
    value = 0

    @factory.sequence
    def param(n):
        return 'param %d' % n

    @factory.sequence
    def description(n):
        return 'description %d' % n

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        """Ensure sequential offset for every AI related to a IED"""
        if not 'offset' in kwargs and 'ied' in kwargs:
            ied = kwargs['ied']
            kwargs['offset'] = ied.ai_set.count()
        return kwargs


class DIFactory(ORMFactory):
    FACTORY_FOR = DI

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        """Ensure sequential offset for every DI related to a IED"""
        if not 'offset' in kwargs and 'ied' in kwargs:
            ied = kwargs['ied']
            kwargs['offset'] = ied.di_set.count()
        return kwargs


class SVFactory(ORMFactory):
    FACTORY_FOR = SV

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        """Ensure sequential offset for every SV related to a IED"""
        if not 'offset' in kwargs and 'ied' in kwargs:
            ied = kwargs['ied']
            kwargs['offset'] = ied.sv_set.count()
        return kwargs


class SVGScreenFactory(ORMFactory):
    FACTORY_FOR = SVGScreen


class SVGElementFactory(ORMFactory):
    FACTORY_FOR = SVGElement


class SVGPropertyChangeSet(ORMFactory):
    FACTORY_FOR = SVGPropertyChangeSet


class FormulaFactory(ORMFactory):
    FACTORY_FOR = Formula

class ColorFactory(ORMFactory):
    FACTORY_FOR = Color
