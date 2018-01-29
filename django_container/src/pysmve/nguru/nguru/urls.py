# encoding: utf-8
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
# from django.views.i18n import javascript_catalog
from apps.mara.admin import site
from apps.api.resources import api
import object_tools


object_tools.autodiscover()

js_info_dict = {
    'packages': ('apps.mara', 'apps.hmi', 'apps.api', ),
}

app_urls = patterns(
    '',
    url(
        '^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'base.html'},
        name='index'),

    url(
        '^login/$',
        'django.contrib.auth.views.login',
        {
            'template_name': 'hmi/login.html'
        },
        name='login',
    ),
    url('^logout/$',
        'django.contrib.auth.views.logout',
        {
            'next_page': '/'
        },
        name='logout'),
    # ========================================================================================
    # Mara application
    # ========================================================================================
    ('^mara/', include('apps.mara.urls')),
    ('^hmi/', include('apps.hmi.urls')),

    # Django URLs in Javascript
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),

    # Tastypie API
    ('^api/', include(api.urls)),

    (
        '^test/$', 'django.views.generic.simple.direct_to_template',
        {'template': 'test.html'}
    ),

    url(r'^admin/', site.urls),

    # ========================================================================================
    # Graphical Query Browser
    # ========================================================================================
    url(r'^qbe/', include('django_qbe.urls')),

    url(r'^admin_tools/', include('admin_tools.urls')),

    (r'^object-tools/', include(object_tools.tools.urls)),
    # FIXME: i18n in JS
    # (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
    (r'^adminactions/', include('adminactions.urls')),
)


urlpatterns = patterns(
    '',
    # Only for local purpouses
    (
        r'^$',
        'django.views.generic.simple.redirect_to',
        {'url': '/%s' % settings.BASE_URL},
    ),
    # URLS de aplicaciones namespaceadas bajo RRHH
    (r'^%s' % settings.BASE_URL, include(app_urls))
)

if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT,
                          show_indexes=True
                          )

    urlpatterns += staticfiles_urlpatterns()
