# encoding: utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from mara.admin import site
urlpatterns = patterns('',
    url("", include('django_socketio.urls')),
#=========================================================================================
# Administración
#=========================================================================================
    (r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', site.urls),
#=========================================================================================
# Indice
#=========================================================================================
    url('^$', 'django.views.generic.simple.direct_to_template',
        {
         'template': 'base.html'
         }),
#=========================================================================================
# Mara application
#=========================================================================================
    ('^mara/', include('mara.urls')),
)
