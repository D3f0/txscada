# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from apps.mara.models import Profile
import json
from forms import ManualFrameInsertForm


@csrf_exempt
def mara_frame_analizer(request):
    '''Mara frame analizer'''
    if not request.method == 'POST':
        form = ManualFrameInsertForm()

    elif request.method == "POST":
        form = ManualFrameInsertForm(request.POST)
        if form.is_valid():
            import ipdb; ipdb.set_trace()
    data = {
        'form': form,
    }
    return render_to_response('mara/mara_frame_analizer.html', data,
                              context_instance=RequestContext(request))


def mara_model_tree(request):
    profile = Profile.objects.get()
    return render_to_response('mara/model_tree.html',
                              {
                                'profile': profile,
                              },
                              context_instance=RequestContext(request))