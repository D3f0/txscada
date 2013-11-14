from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url('^realtime_watch/$', views.realtime_watch, name='realtime_watch'),
    url('^svg_file/(?P<svg_pk>\d+)/$', views.svg_file, name='svg_file'),
    url('^energy_plot/$', 'apps.hmi.views.energy_plot', name='energy_plot'),
)
