from tastypie.api import Api
from tastypie.resources import ModelResource

from apps.mara.models import (Profile, COMaster, IED, SV, DI, AI, Energy,
                              Event, )
from apps.hmi.models import SVGScreen, Formula, SVGElement


class ProfileResource(ModelResource):
    """REST resource for Profile"""
    class Meta:
        resource_name = 'profile'
        queryset = Profile.objects.all()
        allowed_methods = ['get', ]


class COMasterResource(ModelResource):
    """REST resource for COMaster"""
    class Meta:
        resource_name = 'comaster'
        queryset = COMaster.objects.all()
        allowed_methods = ['get', ]


class IEDResource(ModelResource):
    """REST resource for IED"""
    class Meta:
        resource_name = 'ied'
        queryset = IED.objects.all()
        allowed_methods = ['get', ]


class SVResource(ModelResource):
    """REST resource for SV"""
    class Meta:
        resource_name = 'sv'
        queryset = SV.objects.all()
        allowed_methods = ['get', ]


class DIResource(ModelResource):
    """REST resource for DI"""
    class Meta:
        resource_name = 'di'
        queryset = DI.objects.all()
        allowed_methods = ['get', ]


class EventResource(ModelResource):
    """REST resource for Event"""
    class Meta:
        resource_name = 'event'
        queryset = Event.objects.all()
        allowed_methods = ['get', ]

    def dehydrate(self, bundle):
        bundle.data['tag'] = bundle.obj.di.tag
        bundle.data['texto'] = "Un buen texto"
        return bundle


class AIResource(ModelResource):
    """REST resource for AI"""
    class Meta:
        resource_name = 'ai'
        queryset = AI.objects.all()
        allowed_methods = ['get', ]


# class EnergyPointResource(ModelResource):
#     """REST resource for EnergyPoint"""
#     class Meta:
#         resource_name = 'energypoint'
#         queryset = EnergyPoint.objects.all()
#         allowed_methods = ['get', ]


class EnergyResource(ModelResource):
    """REST resource for Energy"""
    class Meta:
        resource_name = 'energy'
        queryset = Energy.objects.all()
        allowed_methods = ['get', ]


class SVGScreenResource(ModelResource):
    """REST resource for SVGScreen"""
    class Meta:
        resource_name = 'svgscreen'
        queryset = SVGScreen.objects.all()
        allowed_methods = ['get', ]

class FormulaResource(ModelResource):
    class Meta:
        resource_name = 'formula'
        queryset = Formula.objects.all()
        allowed_methods = ['get', ]

class SVGElementResource(ModelResource):
    class Meta:
        resource_name = 'svgelement'
        queryset = SVGElement.objects.all()
        allowed_methods = ['get', ]
        limit = 200


api = Api(api_name='v1')

api.register(ProfileResource())
api.register(COMasterResource())
api.register(IEDResource())
api.register(SVResource())
api.register(DIResource())
api.register(EventResource())
api.register(AIResource())
api.register(FormulaResource())
#api.register(EnergyPointResource())
api.register(EnergyResource())
api.register(SVGElementResource())
api.register(SVGScreenResource())
