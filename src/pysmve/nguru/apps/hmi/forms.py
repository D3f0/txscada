# -*- coding: utf-8 -*-
from apps.hmi.models import SVGPropertyChangeSet, SVGScreen
from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import SVGElement, Formula
from django.contrib.auth.models import User, Permission, Group
from django.contrib.admin.widgets import FilteredSelectMultiple
import string


class EnergyDatePlotForm(forms.Form):
    date = forms.DateField(label="Fecha de la curva")
    # estacion = forms.

    def __init__(self, *args, **kwargs):
        super(EnergyDatePlotForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = 'id-plot'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'

        #self.helper.add_input(Submit('submit', 'Submit'))


class SVGScreenAdminForm(forms.ModelForm):
    def __init__(self, *largs, **kwargs):
        super(SVGScreenAdminForm, self).__init__(*largs, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            qs = SVGScreen.objects.filter(profile=instance.profile)
            qs = qs.exclude(pk=instance.pk)
            self.fields['parent'].queryset = qs

    class Meta:
        model = SVGScreen


class SVGScreenForm(forms.Form):

    def __init__(self, *args, **kwargs):
        """Accepts profile as kwarg!"""
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')
        else:
            profile = None
        super(SVGScreenForm, self).__init__(*args, **kwargs)
        qs = self.fields['svg_screen'].queryset
        if profile:
            qs = qs.filter(profile=profile)
        initial = qs.get(parent__isnull=True)
        self.fields['svg_screen'].initial = initial

    svg_screen = forms.ModelChoiceField(SVGScreen.objects.all(),
                                        label=_("SVG Screen"),
                                        empty_label=None)
    ALARM_CHOICES = [(qty, _('%d alarms') % qty) for qty in [3, 5, 7,]]
    alarm_count = forms.ChoiceField(choices=ALARM_CHOICES, initial=5)


def make_svg_change_label(p):
    return "%d %s" % (p.index, p.description)


class SVGElementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SVGElementForm, self).__init__(*args, **kwargs)
    #     self.populate_color_choices()

    # def populate_color_choices(self):
    #     qs = SVGPropertyChangeSet.objects.all()

    #     choices = [('', '--------')]

    #     choices += [
    #         (p.index, make_svg_change_label(p)) for p in qs
    #     ]
    #     self.fields['fill'].choices=choices
    #     self.fields['stroke'].choices=choices


    # fill = forms.IntegerField(
    #                          required=False,
    #                          label=_('fill').title()
    #                         )
    # stroke = forms.IntegerField(
    #                             required=False,
    #                             label=_('stroke').title(),
    #                           )

    def clean_linked_text_change(self):
        screen = self.cleaned_data.get('screen')
        tag = self.cleaned_data.get('tag')
        values = self.cleaned_data.get('linked_text_change')
        for val in values.split(','):
            if val:
                if tag and tag == val:
                    raise forms.ValidationError(_("Can not create a dependency loop"))
                if screen and not screen.elements.filter(tag=val).count():
                    raise forms.ValidationError(_("Tag does not belong to screen"))
        return values

    class Meta:
        model = SVGElement

    class Media:
        css = {
            'all': ('hmi/css/inlineformula.css', )
        }


class FormuluaInlineForm(forms.ModelForm):

    class Meta:
        model = Formula
        widgets = {
            'formula': forms.widgets.TextInput(attrs={'autocomplete': 'off',
                                                      'style': 'width: 100%',
                                                      })
        }
        fields = ('attribute', 'formula', )

MIN_PASS_LEN = 6
MAX_PASS_LEN = 24
EXTRA_PASS_SYMBOLS = u'!"#$%&/()=?¡-_'
VALID_PASS_CHARS = ''.join([string.letters, string.digits, EXTRA_PASS_SYMBOLS])


class UserForm(forms.ModelForm):

    def __init__(self, *largs, **kwargs):
        super(UserForm, self).__init__(*largs, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.fields['pass_1'].required = False
            self.fields['pass_2'].required = False

    pass_1 = forms.CharField(label='Clave', widget=forms.PasswordInput,
                             help_text="Calve de acceso al sistema, la longitud mínima "
                             "son %d caracteres y la máxima %d" % (MIN_PASS_LEN,
                                                                   MAX_PASS_LEN))
    pass_2 = forms.CharField(label='Repetir calve', widget=forms.PasswordInput)

    #user_permissions = forms.ModelMultipleChoiceField(Permission.objects.all())

    def add_error_to_pass_fields(self, message):
        ''' Acceso a bajo nivel de los errores de los campos, sirve para
        poener de manera automática en varios campos un mismo error'''
        error = [message, ]
        self._errors['pass_1'] = self.error_class(error)
        self._errors['pass_2'] = self.error_class(error)

    def clean(self):
        # Contraseña
        pass_1 = self.cleaned_data.get('pass_1')
        pass_2 = self.cleaned_data.get('pass_2')

        # import ipdb; ipdb.set_trace()
        if pass_1 or pass_2:
            # Primero deben ser iguales
            if pass_1 != pass_2:
                self.add_error_to_pass_fields(_("Password should match"))
            else:
                self.is_good_password(pass_1)

        return self.cleaned_data

    def is_good_password(self, clave):
        # Mayor al mínimo
        if len(clave) < MIN_PASS_LEN:
            msg = _('Password should be at least %d character long') % MIN_PASS_LEN
            self.add_error_to_pass_fields(msg)
            return False
        # Menos al maximo
        elif len(clave) > MAX_PASS_LEN:
            msg = _('Password should be at top %d characters long') % MAX_PASS_LEN
            self.add_error_to_pass_fields(msg)
            return False
        # Caracteres validos
        elif not(all(map(lambda c: c in VALID_PASS_CHARS, clave))):
            msg = _('Password can lonly contain letters, numbers and the following '
                    'symbols %s') % EXTRA_PASS_SYMBOLS
            self.add_error_to_pass_fields()
            return False
        # No puede user el nombre de usuario
        else:
            username = self.cleaned_data.get('username')

            if clave.count(username) > 0:
                msg = _('Username can not be included in password')
                self.add_error_to_pass_fields(msg)
                return False
        return True

    def save(self, *largs, **kwargs):
        user = super(UserForm, self).save(*largs, **kwargs)
        try:
            self.instance.pk
            user.set_password(self.cleaned_data['pass_1'])
            user.is_staff = True
        except:
            #_pk = None
            pass
        user.save()
        return user

    class Meta:
        model = User
        exclude = ('password',
                   'user_permissions',
                   )
        widgets = {
            'groups': forms.CheckboxSelectMultiple,
        }


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        widgets = {
            'permissions': FilteredSelectMultiple(_("Permissions"),
                                                  False,
                                                  attrs={'rows': '10'}
                                                  ),
        }
