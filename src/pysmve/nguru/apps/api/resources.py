from tastypie.api import Api
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from apps.mara.models import (Profile, COMaster, IED, SV, DI, AI, Energy,
                              Event)
from apps.hmi.models import SVGScreen, Formula, SVGElement


# API Entry Point
api = Api(api_name='v1')


class ProfileResource(ModelResource):

    """REST resource for Profile"""
    class Meta:
        resource_name = 'profile'
        queryset = Profile.objects.all()
        allowed_methods = ['get', ]
        ordering = SVGElement._meta.get_all_field_names()

api.register(ProfileResource())


class COMasterResource(ModelResource):

    """REST resource for COMaster"""
    class Meta:
        resource_name = 'comaster'
        queryset = COMaster.objects.all()
        allowed_methods = ['get', ]
        ordering = SVGElement._meta.get_all_field_names()

api.register(COMasterResource())


class IEDResource(ModelResource):

    """REST resource for IED"""
    class Meta:
        resource_name = 'ied'
        queryset = IED.objects.all()
        allowed_methods = ['get', ]
        ordering = SVGElement._meta.get_all_field_names()
api.register(IEDResource())


class SVResource(ModelResource):

    """REST resource for SV"""
    class Meta:
        resource_name = 'sv'
        queryset = SV.objects.all()
        allowed_methods = ['get', ]
        ordering = SVGElement._meta.get_all_field_names()
api.register(SVResource())


class DIResource(ModelResource):

    """REST resource for DI"""
    class Meta:
        resource_name = 'di'
        queryset = DI.objects.all()
        allowed_methods = ['get', ]
        ordering = SVGElement._meta.get_all_field_names()
api.register(DIResource())


class EventResource(ModelResource):

    """REST resource for Event"""
    class Meta:
        resource_name = 'event'
        queryset = Event.objects.all()
        allowed_methods = ['get', 'put']
        filtering = {
            'timestamp': ALL,
            'pk': ALL,
            'timestamp_ack': ALL,
        }
        ordering = Event._meta.get_all_field_names()

    def dehydrate(self, bundle):
        bundle.data['tag'] = bundle.obj.di.tag
        bundle.data['texto'] = unicode(bundle.obj)
        return bundle


api.register(EventResource())


class AIResource(ModelResource):

    """REST resource for AI"""
    class Meta:
        resource_name = 'ai'
        queryset = AI.objects.all()
        allowed_methods = ['get', ]
        ordering = SVGElement._meta.get_all_field_names()
api.register(AIResource())


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
        ordering = SVGElement._meta.get_all_field_names()
api.register(EnergyResource())


class SVGScreenResource(ModelResource):

    """REST resource for SVGScreen"""

    profile = fields.ForeignKey(ProfileResource, 'profile')

    class Meta:
        resource_name = 'svgscreen'
        queryset = SVGScreen.objects.all()
        allowed_methods = ['get', ]
        filtering = {
            'name': ALL,
            'id': ALL,
            'profile': ALL,
        }
        ordering = SVGElement._meta.get_all_field_names()
api.register(SVGScreenResource())


class FormulaResource(ModelResource):

    class Meta:
        resource_name = 'formula'
        queryset = Formula.objects.select_related('svg_element')
        allowed_methods = ['get', ]
        ordering = SVGElement._meta.get_all_field_names()

    def dehydrate(self, bundle):
        bundle.data['tag'] = bundle.obj.target.tag
        return bundle


api.register(FormulaResource())


class SVGElementResource(ModelResource):
    '''This resource allows to put updates on the screen'''
    screen = fields.ForeignKey(SVGScreenResource, 'screen')

    class Meta:
        resource_name = 'svgelement'
        queryset = SVGElement.objects.select_related('formula')
        allowed_methods = ['get', ]
        limit = 200
        filtering = {
            'screen': ALL_WITH_RELATIONS,
            'last_update': ALL_WITH_RELATIONS,
            'enabled': ALL_WITH_RELATIONS,
        }
        ordering = SVGElement._meta.get_all_field_names()
        order_by = 'last_update'


    def apply_filters(self, request, applicable_filters):
        #import pdb; pdb.set_trace()
        return super(SVGElementResource, self).apply_filters(request, applicable_filters)

    def dehydrate(self, bundle):
        bundle.data['style'] = bundle.obj.style
        return bundle

api.register(SVGElementResource())




# api.register(EnergyPointResource())
