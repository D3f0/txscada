from django import template

register = template.Library()


@register.filter
def key(an_object, a_key):
    return an_object[a_key]
