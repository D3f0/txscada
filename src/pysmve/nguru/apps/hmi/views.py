# encoding: utf-8

from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.context import RequestContext
from django.db.models.query import Q
from apps.hmi.models import SVGScreen, SVGElement, SVGPropertyChangeSet
from apps.hmi.forms import EnergyDatePlotForm
from django.http import HttpResponse
import json
# Imports para la simulación

from bunch import Bunch


def realtime_watch(request):
    '''Visión de tiempo real'''
    svg = SVGScreen.objects.get()

    return render_to_response('hmi/realtime_watch.html',
                              context_instance=RequestContext(request, {
                                                              'svg': svg,
                                                              })
                              )


def ajax_update(request, svg_pk):

    svg = SVGScreen.objects.get(pk=svg_pk)
    updates = {}
    #from random import sample, randint, choice
    #from string import letters
    # for tag, type_ in sample(svg.tags.items(), randint(1, 10)):

    #     if type_ in ('g', 'rect'):
    #         stroke = '#%s' % ''.join(sample('123456789ABCDEF', 6))
    #         fill = '#%s' % ''.join(sample('123456789ABCDEF', 6))
    #         updates[tag] = {'stroke': stroke, 'fill': fill}
    #     elif type_ == 'text':
    #         text = ''.join(sample(letters, randint(4, 15)))
    #         updates[tag] = {'text': text}
    tags = ['E42SS_03', 'E41SS_03', 'E42II_03', 'E41II_03', 'E4252B03', 'E4152B03', 'E4251_03',]
    for eg in SVGElement.objects.filter(tag__in=tags):
        element_update = Bunch()
        if eg.text:
            element_update['text'] = eg.text
        if eg.background:
            try:
                index = int(eg.background)
            except ValueError:
                print "Error seteando %s con background %s" % (eg, eg.background)
            else:
                change = SVGPropertyChangeSet.objects.get(index=index)
                color = change.background.color
                element_update['fill'] = color
        updates[eg.tag] = element_update



    return HttpResponse(json.dumps(updates), mimetype='application/json')


def energy_plot(request, ):
    form = EnergyDatePlotForm()
    data = {
        'form': form
    }
    return render_to_response('hmi/energy_plot.html',
                              context_instance=RequestContext(request, data)
                              )
