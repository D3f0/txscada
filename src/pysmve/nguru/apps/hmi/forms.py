from apps.hmi.models import SVGPropertyChangeSet, SVGScreen
from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import SVGElement, Formula

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
            qs = SVGScreen.objects.filter(profile = instance.profile)
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
    ALARM_CHOICES = [ (qty, _('%d alarms') % qty) for qty in [3, 5, 7,]]
    alarm_count = forms.ChoiceField(choices=ALARM_CHOICES, initial=5)


def make_svg_change_label(p):
    return "%d %s" % (p.index, p.description)

class SVGElementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SVGElementForm, self).__init__(*args, **kwargs)
        self.populate_color_choices()

    def populate_color_choices(self):
        qs = SVGPropertyChangeSet.objects.all()

        choices = [
            (p.index, make_svg_change_label(p)) for p in qs
        ]
        self.fields['fill'].choices=choices
        self.fields['stroke'].choices=choices


    fill = forms.ChoiceField(required=False)
    stroke = forms.ChoiceField(required=False)

    def clean_linked_text_change(self):
        screen = self.cleaned_data.get('screen')
        tag = self.cleaned_data.get('tag')
        val = self.cleaned_data.get('linked_text_change')
        if val:
            if tag and tag == val:
                raise forms.ValidationError(_("Can not create a dependency loop"))
            if screen and not screen.elements.filter(tag=val).count():
                raise forms.ValidationError(_("Tag does not belong to screen"))
        return val

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
            'formula': forms.widgets.TextInput(attrs={'autocomplete':'off',
                                                      'style': 'width: 100%',})
        }
        fields = ('attribute', 'formula', )
