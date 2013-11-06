# encoding: utf-8

import json

from apps.hmi.forms import EnergyDatePlotForm
from apps.hmi.models import SVGElement, SVGPropertyChangeSet, SVGScreen
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.context import RequestContext

# Imports para la simulación



def realtime_watch(request):
    '''Visión de tiempo real'''
    svg = SVGScreen.objects.latest('pk')

    return render_to_response('hmi/realtime_watch.html',
                              context_instance=RequestContext(request, {
                                                              'svg': svg,
                                                              })
                              )



def energy_plot(request, ):
    form = EnergyDatePlotForm()
    data = {
        'form': form
    }
    return render_to_response('hmi/energy_plot.html',
                              context_instance=RequestContext(request, data)
                              )
