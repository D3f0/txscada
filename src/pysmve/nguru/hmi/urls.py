from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
                       url('^realtime_watch/$',
                           'hmi.views.realtime_watch',
                           name='realtime_watch'),
                       )
