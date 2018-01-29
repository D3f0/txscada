from django.conf.urls.defaults import *
from resources import api


urlpatterns = patterns('',
    (r'^v1/', include(api.urls)),
)