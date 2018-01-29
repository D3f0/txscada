from django import template
import json


register = template.Library()


@register.simple_tag(takes_context=True)
def user_perm_array(context):
    user = context['user']
    perms = list(user.get_all_permissions())
    print "Dumping perms", perms
    return json.dumps(perms)

