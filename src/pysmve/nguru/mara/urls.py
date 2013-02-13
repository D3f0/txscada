# coding: utf-8

from django.conf.urls import patterns, url

urlpatterns = patterns('',

    # Análisis de tramas mara
    url(r'mara_frame_analizer',
        'mara.views.mara_frame_analizer',
        name='mara_frame_analizer'),
)
