from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
                       url('^realtime_watch/$',
                           'apps.hmi.views.realtime_watch',
                           name='realtime_watch'),
                       url('^ajax_update/(?P<svg_pk>\d+)/?$',
                           'apps.hmi.views.ajax_update',
                           name='ajax_update'),
                       )
