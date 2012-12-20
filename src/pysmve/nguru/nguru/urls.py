from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from mara.admin import site
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'nguru.views.home', name='home'),
    # url(r'^nguru/', include('nguru.foo.urls')),
    url("", include('django_socketio.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin', site.urls),
    url('^$', 'django.views.generic.simple.direct_to_template',
        {
         'template': 'index.html'
         })
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
