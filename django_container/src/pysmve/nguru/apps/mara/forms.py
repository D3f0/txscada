# -*- coding: utf-8 -*-
from django import forms
from models import COMaster
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class ManualFrameInsertForm(forms.Form):
    co_master = forms.ModelChoiceField(COMaster.objects.all())
    frame = forms.CharField(widget=forms.Textarea(attrs={'cols': 100,
                            'class': 'field span9',
                            'placeholder': _('Paste frame here')}))

    def clean_frame(self):
        data = self.cleaned_data.get('frame')
        frame = COMaster._frame_regex.search(data)
        if not frame:
            raise ValidationError("Trama Inválida")
        return frame.group()  # Test match
