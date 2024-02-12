from django import forms

from service.models import PerformerGroup
class PerformerGroupForm(forms.ModelForm):
    class Meta:
        model = PerformerGroup
        fields = ['name', 'description', ]