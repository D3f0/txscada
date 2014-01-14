from django.conf.urls import patterns, include
from resources import api


urlpatterns = patterns('',
    (r'^v1/', include(api.urls)),
)