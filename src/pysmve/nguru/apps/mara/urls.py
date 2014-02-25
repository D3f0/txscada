# coding: utf-8

from django.conf.urls import patterns, url
#from .updates import register

urlpatterns = patterns(
    'apps.mara.views',
    url(r'^mara_frame_analizer/$',
        'mara_frame_analizer',
        name='mara_frame_analizer'),
    url('^mara_model_tree/$',
        'mara_model_tree',
        name='mara_model_tree'),
)


#egister()
