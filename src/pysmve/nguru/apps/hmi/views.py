# encoding: utf-8

from apps.hmi.forms import EnergyDatePlotForm
from apps.hmi.models import SVGScreen
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
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


def svg_file(request, svg_pk):
    """Gets static file URL for SVG file"""
    svg_screen = get_object_or_404(SVGScreen, pk=svg_pk)
    return HttpResponseRedirect(svg_screen.svg.url)
