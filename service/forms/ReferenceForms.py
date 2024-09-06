from service.models import Reference, ReferenceItem
from django import forms


class ReferenceForm(forms.ModelForm):
    """
    Форма для создания и редактирования справочников.
    """
    class Meta:
        model = Reference
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название справочника'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
        }


class ReferenceItemForm(forms.ModelForm):
    """
    Форма для создания и редактирования элементов справочника.
    """
    class Meta:
        model = ReferenceItem
        fields = ['value']  # Убрано поле 'reference'
        widgets = {
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Значение'}),
        }