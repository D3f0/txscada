from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from apps.hmi.models import SVGScreen
from django.utils.translation import ugettext_lazy as _


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
