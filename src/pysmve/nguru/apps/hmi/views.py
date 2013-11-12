# encoding: utf-8

from apps.hmi.forms import EnergyDatePlotForm
from django.shortcuts import render_to_response
from django.template.context import RequestContext

# Imports para la simulación


def realtime_watch(request):
    '''Visión de tiempo real'''
    from forms import SVGScreenForm
    form = SVGScreenForm()

    return render_to_response('hmi/realtime_watch.html',
                              context_instance=RequestContext(request, {
                                                              'form': form,
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
