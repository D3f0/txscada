# Create your views here.
from models import Profile
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext

def profile_tree(request, name):
    '''Shows a profile tree'''
    profile = get_object_or_404(Profile, name=name)
    data = dict(profile=profile)
    return render_to_response('tree.html',
                              data,
                              context_instance=RequestContext(request)
                              )
