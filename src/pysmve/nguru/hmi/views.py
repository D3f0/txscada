# encoding: utf-8

from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.context import RequestContext

def realtime_watch(request):
    '''Visión de tiempo real'''
    return render_to_response('hmi/realtime_watch.html',
        context_instance = RequestContext(request, {})
        )
