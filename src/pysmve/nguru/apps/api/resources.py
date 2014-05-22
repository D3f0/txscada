# -*- coding: utf-8 -*-

from apps.hmi.models import Formula, SVGElement, SVGScreen
from apps.mara.models import AI, COMaster, DI, Energy, Event, IED, Profile, SV
from tastypie import fields
from tastypie.api import Api
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import (BasicAuthentication, ApiKeyAuthentication,
                                     SessionAuthentication, MultiAuthentication)

from tastypie.resources import ALL, ALL_WITH_RELATIONS, ModelResource
from tastypie.exceptions import NotFound, BadRequest
from datetime import datetime

# API Entry Point
api = Api(api_name='v1')
authentication = MultiAuthentication(
                                     #BasicAuthentication(),
                                     SessionAuthentication())
authorization = DjangoAuthorization()


class ProfileResource(ModelResource):

    """REST resource for Profile"""
    class Meta:
        resource_name = 'profile'
        queryset = Profile.objects.all()
        allowed_methods = ['get', ]
        ordering = Profile._meta.get_all_field_names()
        authentication = authentication
        authorization = authorization

api.register(ProfileResource())


class COMasterResource(ModelResource):

    """REST resource for COMaster"""
    class Meta:
        resource_name = 'comaster'
        queryset = COMaster.objects.all()
        allowed_methods = ['get', ]
        ordering = COMaster._meta.get_all_field_names()

api.register(COMasterResource())


class IEDResource(ModelResource):

    """REST resource for IED"""
    class Meta:
        resource_name = 'ied'
        queryset = IED.objects.all()
        allowed_methods = ['get', ]
        ordering = IED._meta.get_all_field_names()
api.register(IEDResource())


class SVResource(ModelResource):

    """REST resource for SV"""
    class Meta:
        resource_name = 'sv'
        queryset = SV.objects.all()
        allowed_methods = ['get', ]
        ordering = SV._meta.get_all_field_names()
api.register(SVResource())


class DIResource(ModelResource):

    """REST resource for DI"""
    class Meta:
        resource_name = 'di'
        queryset = DI.objects.all()
        allowed_methods = ['get', ]
        ordering = DI._meta.get_all_field_names()
        filtering = {
            'tag': ALL,
        }
api.register(DIResource())


class EventResourceAuthorization(DjangoAuthorization):
    def update_detail(self, object_list, bundle):
        """
        Returns either ``True`` if the user is allowed to update the object in
        question or throw ``Unauthorized`` if they are not.

        Returns ``True`` by default.
        """
        from ipdb import set_trace; set_trace()
        return True


class EventResource(ModelResource):

    """REST resource for Event"""
    di = fields.ForeignKey(DIResource, 'di')

    class Meta:
        resource_name = 'event'
        queryset = Event.objects.filter(show=True).select_related('di__ied__co_master__profile')
        allowed_methods = ['get', 'put']
        filtering = {
            'timestamp': ALL,
            'pk': ALL,
            'timestamp_ack': ALL,
            'di': ALL_WITH_RELATIONS,
        }
        ordering = Event._meta.get_all_field_names()
        authorization = EventResourceAuthorization()
        authentication = authentication
        order_by = ('-timestamp')

    def dehydrate(self, bundle):
        bundle.data['tag'] = bundle.obj.di.tag
        bundle.data['texto'] = unicode(bundle.obj)
        return bundle

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        #import ipdb; ipdb.set_trace()
        if not bundle.obj or not self.get_bundle_detail_data(bundle):
            try:
                lookup_kwargs = self.lookup_kwargs_with_identifiers(bundle, kwargs)
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs

            try:
                bundle.obj = self.obj_get(bundle=bundle, **lookup_kwargs)
            except Event.ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)

        if bundle.data.get('timestamp_ack', None) == 'now':
            bundle.data['timestamp_ack'] = datetime.now()

        bundle = self.full_hydrate(bundle)
        return self.save(bundle, skip_errors=skip_errors)

    def obj_get_list(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_get_list``.

        Takes an optional ``request`` object, whose ``GET`` dictionary can be
        used to narrow the query.
        """
        filters = {}

        if hasattr(bundle.request, 'GET'):
            # Grab a mutable copy.
            filters = bundle.request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)
        applicable_filters = self.build_filters(filters=filters)

        try:
            objects = self.apply_filters(bundle.request, applicable_filters)
            return self.authorized_read_list(objects, bundle)
        except ValueError:
            raise BadRequest("Invalid resource lookup data provided (mismatched type).")


api.register(EventResource())


class AIResource(ModelResource):

    """REST resource for AI"""
    class Meta:
        resource_name = 'ai'
        queryset = AI.objects.all()
        allowed_methods = ['get', ]
        ordering = AI._meta.get_all_field_names()
        filtering = {
            'id': ALL,
        }
api.register(AIResource())


# class EnergyPointResource(ModelResource):
#     """REST resource for EnergyPoint"""
#     class Meta:
#         resource_name = 'energypoint'
#         queryset = EnergyPoint.objects.all()
#         allowed_methods = ['get', ]


class EnergyResource(ModelResource):

    """REST resource for Energy"""

    ai = fields.ForeignKey(AIResource, 'ai')

    class Meta:
        resource_name = 'energy'
        queryset = Energy.objects.select_related('ai')
        allowed_methods = ['get', ]
        ordering = Energy._meta.get_all_field_names()
        filtering = {
            'timestamp': ALL,
            'ai': ALL_WITH_RELATIONS,
            'code': ALL,
        }

    def alter_list_data_to_serialize(self, request, data):
        '''Add unit for plotting energy'''
        ai_pk = request.REQUEST.get('ai__id')
        if ai_pk:
            ai = AI.objects.get(pk=ai_pk)
            channel = ai.channel
            data['meta'].update(unit=('MW' if channel == 0 else 'MVAR'),
                                escala_e=ai.escala_e)


        return data

    def dehydrate(self, bundle):
        '''This values are used to plot energy with D3'''
        eng_value = bundle.obj.value * bundle.obj.ai.escala_e
        bundle.data['eng_value'] = eng_value
        bundle.data['repr_value'] = '%s %s' % (eng_value, bundle.obj.ai.unit)

        return bundle

api.register(EnergyResource())


class SVGScreenResource(ModelResource):

    """REST resource for SVGScreen"""

    profile = fields.ForeignKey(ProfileResource, 'profile')
    parent = fields.ForeignKey('self', 'parent', null=True, blank=True)

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
        ordering = Formula._meta.get_all_field_names()

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
        allowed_methods = ['get', 'put', ]
        limit = 1000
        filtering = {
            'screen': ALL_WITH_RELATIONS,
            'last_update': ALL_WITH_RELATIONS,
            'enabled': ALL_WITH_RELATIONS,
        }
        ordering = SVGElement._meta.get_all_field_names()
        order_by = 'last_update'
        authorization = authorization

    def _obj_update(self, *args, **kwargs):

        import ipdb; ipdb.set_trace()
        return super(SVGElementResource, self).obj_update(*args, **kwargs)

    def dehydrate(self, bundle):
        bundle.data['style'] = bundle.obj.style
        return bundle

api.register(SVGElementResource())


class SVGElementDetailResource(ModelResource):
    """This resource provides all data related to screen resources
    It's requested by realtime monitoring javascript app upon start."""
    screen = fields.ForeignKey(SVGScreenResource, 'screen')
    on_click_jump = fields.ForeignKey(SVGScreenResource,
                                      'on_click_jump',
                                      blank=True,
                                      null=True,
                                      )

    formulas = fields.ToManyField(FormulaResource, 'formula_set', full=True)

    def dehydrate(self, bundle):
        #bundle.data['formulas'] = bundle.obj.formulas
        bundle.data['linked_text_change'] = bundle.obj.linked_text_change_dict
        return bundle

    class Meta:
        resource_name = 'svgelementdetail'
        queryset = SVGElement.objects.select_related('formula', 'screen')
        allowed_methods = ['get', ]
        limit = 200
        filtering = {
            'screen': ALL_WITH_RELATIONS,
            'last_update': ALL_WITH_RELATIONS,
            'enabled': ALL_WITH_RELATIONS,
            'on_click_jump': ALL,
        }
        ordering = SVGElement._meta.get_all_field_names()
        order_by = 'last_update'

api.register(SVGElementDetailResource())



# api.register(EnergyPointResource())
