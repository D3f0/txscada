# encoding: utf-8

from apps.hmi.models import SVGScreen
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
import json
from django.core.serializers.json import DjangoJSONEncoder
from apps.mara.models import Profile, COMaster, Energy, AI
import calendar
from datetime import date, datetime, timedelta
from django.db.models.aggregates import Count
from collections import OrderedDict
from cStringIO import StringIO


@permission_required('hmi.can_view_realtime')
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
    # TODO: Filter by profile
    data = {
        'comasters': COMaster.objects.all().order_by('-pk'),
        'ais': AI.objects.exclude(unit__iendswith='v'),
        'today': date.today(),
    }
    return render_to_response('hmi/energy_plot.html',
                              context_instance=RequestContext(request, data)
                              )


def _validate_date_range(date_from, date_to):
    '''
    date_from and date_to have the 2013-1-1 format
    '''
    try:
        year, month, day = map(int, date_from.split('-'))
        date_from = datetime(year, month, day, 0, 0, 0)
    except ValueError:
        raise ValueError("Invalid from date")
    try:
        year, month, day = map(int, date_to.split('-'))
        date_to = datetime(year, month, day, 23, 59, 59, 9999)
    except ValueError:
        raise ValueError("Invalid to date")
    if date_from > date_to:
        raise ValueError("From date is after to date")
    return date_from, date_to


def energy_export(request, ai_pk, date_from, date_to):
    '''Generates export of energy values of one AI
    i.e:
    05/11/13,11:45,0.1200,0.0814
    05/11/13,12:00,0.0776,0.0534
    '''

    ai = get_object_or_404(AI, pk=ai_pk)
    try:
        date_from, date_to = _validate_date_range(date_from, date_to)
    except ValueError as e:
        return HttpResponseBadRequest(e)
    try:
        other_ai = ai.ied.ai_set.exclude(channel=ai.channel).get()
    except (AI.DoesNotExist, AI.MultipleObjectsReturned):
        return HttpResponseBadRequest("Invalid AI looking for the other channel")
    # Sort by channel
    if ai.channel == 0:
        ai_active, ai_reactive = ai, other_ai
    elif ai.channel == 1:
        ai_active, ai_reactive = other_ai, ai
    else:
        return HttpResponseBadRequest("AI channel missmatch")
    values = ('timestamp', 'value', 'ai__escala')
    active = ai_active.energy_set.filter(timestamp__gte=date_from,
                                         timestamp__lte=date_to)

    active = active.exclude(code=1).values(*values).order_by('timestamp')
    reactive = ai_reactive.energy_set.filter(timestamp__gte=date_from,
                                             timestamp__lte=date_to).values(*values)
    reactive = reactive.exclude(code=1).values(*values).order_by('timestamp')
    if not active.count() or not reactive.count():
        return HttpResponseBadRequest("No records")
    output = StringIO()
    for v1, v2 in zip(active, reactive):
        row_date = v1['timestamp']
        output.write('%s,%s,%s,%s\n' % (
                     row_date.strftime('%d/%m/%y'),
                     row_date.strftime('%H:%M') if row_date.minute != 59 else '24:00',
                     v1['value'],
                     v2['value']
                     ))

    response = HttpResponse(output.getvalue(), content_type='text/plain')
    content_disposition = 'attachment; filename=%s.txt' % ai_active.tag
    response['Content-Disposition'] = content_disposition
    return response


def max_energy_period(request, ai_pk, date_from, date_to):
    '''
    Returns JSON with the maximum value of energy in a period
    '''
    ai = get_object_or_404(AI, pk=ai_pk)
    try:
        date_from, date_to = _validate_date_range(date_from, date_to)
    except ValueError as e:
        return HttpResponseBadRequest(e)
    try:
        other_ai = ai.ied.ai_set.exclude(channel=ai.channel).get()
    except (AI.DoesNotExist, AI.MultipleObjectsReturned):
        return HttpResponseBadRequest("Invalid AI looking for the other channel")
    # Sort by channel
    if ai.channel == 0:
        ai_active, ai_reactive = ai, other_ai
    elif ai.channel == 1:
        ai_active, ai_reactive = other_ai, ai
    else:
        return HttpResponseBadRequest("AI channel missmatch")
    active = ai_active.energy_set.filter(timestamp__gte=date_from,
                                         timestamp__lte=date_to)
    reactive = ai_reactive.energy_set.filter(timestamp__gte=date_from,
                                             timestamp__lte=date_to)
    max_active = active.exclude(hnn=True).order_by('-value')[0]
    max_reactive = reactive.filter(timestamp=max_active.timestamp).get()

    ing_active = max_active.value * max_active.ai.escala
    ing_reactive = max_reactive.value * max_reactive.ai.escala
    # Pythagorean theorem
    value = ((ing_active ** 2) + (ing_reactive ** 2)) ** 0.5
    data = {
        'value_active': max_active.value,
        'value_reactive': max_reactive.value,
        'timestamp': max_active.timestamp,
        'ing_active': ing_active,
        'ing_reactive': ing_reactive,
        'value': value
    }
    json_data = json.dumps(data, cls=DjangoJSONEncoder)
    return HttpResponse(json_data, content_type='application/json')


def svg_file(request, svg_pk):
    """Gets static file URL for SVG file"""
    svg_screen = get_object_or_404(SVGScreen, pk=svg_pk)
    return HttpResponseRedirect(svg_screen.svg.url)


def formula_calc(request):
    """This view is meant for debugging formula calc bakend"""
    pass


@permission_required('mara.can_see_month_report')
def month_energy_report(request, year=None, month=None):
    today = date.today()
    try:
        year, month = int(year), int(month)
        start_date = date(year, month, 1)
    except (ValueError, TypeError):
        url = reverse('month_energy_report', kwargs={'month': today.month,
                                                     'year': today.year})
        return HttpResponseRedirect(url)

    cal = calendar.Calendar()
    daterange = [ d for d in cal.itermonthdates(year, month) if d.month == month ]

    comaster_month_energies = {}
    date_from = datetime(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    date_to = datetime(year, month, last_day, 23, 59, 59)


    # COMaster -> AI
    for comaster in COMaster.objects.all():
        ai_qs = AI.objects.filter(ied__co_master=comaster).order_by('ied__pk', 'pk')

        if not ai_qs.count():
            continue
        ais = comaster_month_energies.setdefault(comaster, OrderedDict())
        for n, ai in enumerate(ai_qs):
            by_date = ais.setdefault(ai, {})
            ai_measures = Energy.objects.filter(ai=ai,
                                                timestamp__gte=date_from,
                                                timestamp__lte=date_to)
            ai_measures = ai_measures.extra({'d': 'date(timestamp)'})
            ai_measures = ai_measures.values('d').annotate(count=Count('id'))
            for date_count in ai_measures:
                by_date[date_count['d']] = date_count['count']

    # Previous and next links
    prev_url, next_url = None, None

    prev_date = date_from - timedelta(days=1)
    if Energy.objects.filter(timestamp__lte=prev_date).count():
        prev_url = reverse('month_energy_report', kwargs={'month': prev_date.month,
                                                          'year': prev_date.year})
    next_date = date(year, month, last_day) + timedelta(days=1)
    if next_date < today:
        next_url = reverse('month_energy_report', kwargs={'month': next_date.month,
                                                          'year': next_date.year})


    period = start_date.strftime('%m/%y')
    data = {
        'energy_dict': comaster_month_energies,
        'daterange': daterange,
        'prev_url': prev_url,
        'next_url': next_url,
        'period': period,
    }
    return render_to_response('hmi/month_energy_report.html',
                              context_instance=RequestContext(request, data))
