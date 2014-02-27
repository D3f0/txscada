# Create your views here.

import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from apps.mara.models import Profile
from apps.mara.forms import ManualFrameInsertForm


@csrf_exempt
def mara_frame_analizer(request):
    '''Mara frame analizer'''
    message_text, message_class = None, None

    if not request.method == 'POST':
        form = ManualFrameInsertForm()

    elif request.method == "POST":
        form = ManualFrameInsertForm(request.POST)
        if form.is_valid():
            co_master = form.cleaned_data['co_master']
            frame = form.cleaned_data['frame']
            if co_master._process_str_frame(frame):
                message_text, message_class = _("OK"), 'success'
            else:
                message_text, message_class = _("Error"), 'error'
    data = {
        'form': form,
        'message_text': message_text,
        'message_class': message_class,
    }
    return render_to_response('mara/mara_frame_analizer.html', data,
                              context_instance=RequestContext(request))


def mara_model_tree(request):
    profile = Profile.objects.get()
    data = {
        'profile': profile,
    }
    return render_to_response('mara/model_tree.html', data,
                              context_instance=RequestContext(request))
