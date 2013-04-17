# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def mara_frame_analizer(request):
    '''Mara frame analizer'''
    if request.method == "POST":
        hexstr = request.POST.get('data')
        data = {'a': 1, 'b': 2}
        dump = json.dumps(data)
        return HttpResponse(dump, )
        # NO mandamos el texto

    return render_to_response('mara/mara_frame_analizer.html', {},
                              context_instance=RequestContext(request))