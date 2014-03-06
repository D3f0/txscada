import factory
from factory.django import DjangoModelFactory as ORMFactory
from django.contrib.contenttypes.models import ContentType
from apps.mara.models import (Profile, COMaster, IED, AI, DI, SV
                              #, Energy, Event, ComEvent)
                              )


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
    ip_address = factory.Sequence(lambda n: '192.168.1.%d' % (n + 1))
    enabled = True
    description = factory.LazyAttribute(lambda s: 'Description for %s' % s.ip_address)


class IEDFactory(ORMFactory):
    FACTORY_FOR = IED
    co_master = factory.SubFactory(COMasterFactory)
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

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        """Ensure sequential offset for every AI related to a IED"""
        if not 'offset' in kwargs and 'ied' in kwargs:
            ied = kwargs['ied']
            kwargs['offset'] = ied.ai_set.count()
        return kwargs


class DIFactory(ORMFactory):
    FACTORY_FOR = DI


class SVFactory(ORMFactory):
    FACTORY_FOR = SV
