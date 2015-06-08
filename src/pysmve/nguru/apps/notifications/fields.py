# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import EmailValidator, EMPTY_VALUES
from django.db.models import TextField
import re

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)


class CommaSeparatedEmailField(TextField):
    description = _(u"E-mail address(es)")

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token", ",")
        invalid_email_message = kwargs.pop(
            'invalid_email_message',
            u"Itroduzca una dirección de email válida"
        )
        self.validator = EmailValidator(email_re, invalid_email_message)
        super(CommaSeparatedEmailField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return []

        value = [item.strip() for item in value.split(self.token) if item.strip()]

        return list(set(value))

    def clean(self, value, instance):
        """
        Check that the field contains one or more 'comma-separated' emails
        and normalizes the data to a list of the email strings.
        """
        value = self.to_python(value)

        if value in EMPTY_VALUES and self.required:
            raise forms.ValidationError(_(u"This field is required."))

        for email in value:
            self.validator(email)
        return value

try:

    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^apps\.notifications\.fields\.CommaSeparatedEmailField"])
except ImportError:
    pass
