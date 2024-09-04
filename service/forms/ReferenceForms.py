from service.models import Book, BookItem
from django import forms


class ReferenceForm(forms.ModelForm):
    """
    Форма для создания и редактирования справочников.
    """
    class Meta:
        model = Book
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название справочника'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
        }


class ReferenceItemForm(forms.ModelForm):
    """
    Форма для создания и редактирования элементов справочника.
    """
    class Meta:
        model = BookItem
        fields = ['reference', 'value',]
        widgets = {
            'reference': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Значение'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }