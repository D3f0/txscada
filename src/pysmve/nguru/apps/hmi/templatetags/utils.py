from django import template
from apps.hmi.models import SVGScreen
from django.core.urlresolvers import reverse


register = template.Library()

@register.filter
def getitem(item, key):
    return item.get(key,'-')

weekend = set([5, 6])

@register.simple_tag
def add_class_if_weekend(a_date, a_css_class):
    if a_date.weekday() in weekend:
        return a_css_class
    return ''


@register.simple_tag(takes_context=True)
def screen_menu_html(context):
    '''Generate
        li>a[href]
    data for screens
    '''
    base_link = reverse('realtime_watch')

    def link_to_screen(screen):
        link = '?'.join((base_link, 'screen_pk=%s' % screen.pk, ))
        return '<li><a href="%s">%s</a></li>' % (link, screen)

    screens = SVGScreen.objects.order_by('-parent', 'name')
    return '\n'.join([link_to_screen(s) for s in screens])
