# encoding: utf-8

from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.context import RequestContext
from apps.hmi.models import SVGScreen
from django.http import HttpResponse
import json

def realtime_watch(request):
    '''Visión de tiempo real'''
    svg = SVGScreen.objects.get()

    return render_to_response('hmi/realtime_watch.html',
        context_instance = RequestContext(request, {
            'svg': svg,
            })
        )


def ajax_update(request, svg_pk):
    from random import sample, randint, choice
    from string import letters
    svg = SVGScreen.objects.get(pk=svg_pk)
    updates = {}
    for tag, type_ in sample(svg.tags.items(), randint(1, 10)):

        if type_ in ('g', 'rect'):
            stroke = '#%s' % ''.join(sample('123456789ABCDEF', 6))
            fill = '#%s' % ''.join(sample('123456789ABCDEF', 6))
            updates[tag] = {'stroke': stroke, 'fill': fill}
        elif type_ == 'text':
            text = ''.join(sample(letters, randint(4,15)))
            updates[tag] = {'text': text}


    return HttpResponse(json.dumps(updates), mimetype='application/json')
