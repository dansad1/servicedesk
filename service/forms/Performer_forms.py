from django import forms
from service.models import PerformerGroup


class PerformerGroupForm(forms.ModelForm):
    class Meta:
        model = PerformerGroup
        fields = ['name', 'description', ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название группы'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите описание группы'}),
        }