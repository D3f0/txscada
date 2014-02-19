import factory

from apps.mara.models import Profile, COMaster, IED



class ProfileFactory(factory.Factory):
    FACTORY_FOR = Profile

class COMasterFactory(factory.Factory):
    FACTORY_FOR = COMaster

class IEDFactory(factory.Factory):
    FACTORY_FOR = IED