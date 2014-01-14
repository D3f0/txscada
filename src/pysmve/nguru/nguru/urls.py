# encoding: utf-8
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from apps.mara.admin import site, config_site
from apps.api.resources import api
from django.views.generic.base import TemplateView
from nguru.utils.views import URLBasedTemplateView
import object_tools


object_tools.autodiscover()


urlpatterns = patterns('',
    #===========================================================================
    # Index
    #===========================================================================
    url('^$',
        TemplateView.as_view(template_name='base.html'),
        name='index'),

    url('^login/$',
        'django.contrib.auth.views.login',
        {
            'template_name': 'hmi/login.html'
        },
        name='login',
    ),
    #===========================================================================
    # Mara application
    #===========================================================================
    ('^mara/', include('apps.mara.urls')),
    ('^hmi/', include('apps.hmi.urls')),

    # Django URLs in Javascript
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),

    # Tastypie API
    ('^api/', include(api.urls)),

    #===========================================================================
    # Mapeo directo a templates
    #===========================================================================
    # url('^sockjsdemo/', {
    #         'template': 'websocket-demo.html',
    #     }, name='websocket_demo'),
    #===========================================================================
    # Administración
    #===========================================================================
    #(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', site.urls),
    url(r'^config/', config_site.urls),

    #===========================================================================
    # Graphical Query Browser
    #===========================================================================
    #url(r'^qbe/', include('django_qbe.urls')),
    # Disabled due 1.6 incompatibilty

    url(r'^admin_tools/', include('admin_tools.urls')),
    #===========================================================================
    # Django object tools
    #===========================================================================
    (r'^object-tools/', include(object_tools.tools.urls)),
)

if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT,
                          show_indexes=True
                          )

    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG and False:
    urlpatterns += patterns('',
        (r'^(?P<template_name>.*\.html)/?$', URLBasedTemplateView.as_view(), ),
    )


