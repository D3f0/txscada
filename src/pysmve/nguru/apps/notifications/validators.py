from django.core.exceptions import ValidationError
from django.template import Template, Context


def validate_template_format(template_string):
    """Validates template django format"""
    # TODO: Fix possible ORM DML access
    try:
        template = Template(template_string)
        template.render(Context())
    except Exception as e:
        raise ValidationError(unicode(e))
