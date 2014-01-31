from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url('^realtime_watch/$', views.realtime_watch, name='realtime_watch'),
    url('^svg_file/(?P<svg_pk>\d+)/$', views.svg_file, name='svg_file'),
    url('^energy_plot/$', 'apps.hmi.views.energy_plot', name='energy_plot'),
    url('^month_report/(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        'apps.hmi.views.month_energy_report',
        name='month_energy_report'),
    url('^month_report/$', 'apps.hmi.views.month_energy_report',
        name='month_energy_report'),
)
