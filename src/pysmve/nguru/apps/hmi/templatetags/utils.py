from django import template

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
