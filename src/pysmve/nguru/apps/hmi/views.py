# encoding: utf-8

from apps.hmi.forms import EnergyDatePlotForm
from apps.hmi.models import SVGScreen
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required



@login_required(login_url='/login')
def realtime_watch(request):
    """Real time monitoring"""
    # This view could be well be sent to a generic template View.
    # It's kept like a function based view for historical reasons.
    #from forms import AlarmFilterForm
    #alarm_filter_form = AlarmFilterForm()
    context = {
      #'alarm_filter_form': alarm_filter_form
    }
    return render_to_response('hmi/realtime_watch.html',
                              context_instance=RequestContext(request, context)
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


def formula_calc(request):
    """This view is meant for debugging formula calc bakend"""
    pass

