from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'profile/(?P<name>[\d\w]+)', 'mara.views.profile_tree',
        name='profile_tree'),
)
