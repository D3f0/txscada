# encoding: utf-8
from django.conf.urls import patterns, include, url

from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from mara.admin import site
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
    ('^mara/', include('mara.urls')),
    ('^hmi/', include('hmi.urls')),

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
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^(?P<template>.*)/?$', 'django.views.generic.simple.direct_to_template', ),
    )
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# urlpatterns += staticfiles_urlpatterns()
