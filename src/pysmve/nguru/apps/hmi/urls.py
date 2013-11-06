from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
                       url('^realtime_watch/$',
                           'apps.hmi.views.realtime_watch',
                           name='realtime_watch'),
                       url('^energy_plot/$',
                           'apps.hmi.views.energy_plot',
                           name='energy_plot'),
                       )
