# encoding: utf-8
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from apps.mara.admin import site
from apps.api.resources import api


import object_tools

object_tools.autodiscover()


urlpatterns = patterns('',

    #=========================================================================================
    # Index
    #=========================================================================================
    url('^$', 'django.views.generic.simple.direct_to_template',
        {
         'template': 'base.html'
         }),
    #=========================================================================================
    # Mara application
    #=========================================================================================
    ('^mara/', include('apps.mara.urls')),
    ('^hmi/', include('apps.hmi.urls')),
    ('^api/', include(api.urls)),

    #=========================================================================================
    # Mapeo directo a templates
    #=========================================================================================
    url('^sockjsdemo/', 'django.views.generic.simple.direct_to_template', {
            'template': 'websocket-demo.html'
        }, name='websocket_demo'),
    #=========================================================================================
    # Administración
    #=========================================================================================
    (r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', site.urls),
    #=========================================================================================
    # Graphical Query Browser
    #=========================================================================================
    url(r'^qbe/', include('django_qbe.urls')),

    url(r'^admin_tools/', include('admin_tools.urls')),
    #=========================================================================================
    # Django object tools
    #=========================================================================================
    (r'^object-tools/', include(object_tools.tools.urls)),
)

if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT,
                          show_indexes=True
                          )

    urlpatterns += staticfiles_urlpatterns()

# if settings.DEBUG:
#     urlpatterns += patterns('',
#         (r'^(?P<template>.*)/?$', 'django.views.generic.simple.direct_to_template', ),
#     )


