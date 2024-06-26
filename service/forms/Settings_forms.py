from django import forms
from service.models import Status, Priority, RequestType, PriorityDuration, StatusTransition, FieldMeta
from colorfield.fields import ColorField, ColorWidget

class RequestTypeForm(forms.ModelForm):
    fields = forms.ModelMultipleChoiceField(
        queryset=FieldMeta.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Поля'
    )

    class Meta:
        model = RequestType
        fields = ['name', 'description', 'fields']


class PriorityForm(forms.ModelForm):
    class Meta:
        model = Priority
        fields = ['name']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
        }
        
class PriorityDurationForm(forms.ModelForm):
    class Meta:
        model = PriorityDuration
        fields = ['request_type', 'priority', 'duration_in_hours']

        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'duration_in_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите количество часов'}),
        }

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name', 'color', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            'color': ColorWidget(attrs={'id': 'id_color'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите описание'}),
            
        }
        
    def __init__(self, *args, **kwargs):
        super(StatusForm, self).__init__(*args, **kwargs)


class StatusTransitionForm(forms.ModelForm):
    class Meta:
        model = StatusTransition
        fields = ['from_status', 'to_status', 'allowed_groups']

        widgets = {
            'from_status': forms.Select(attrs={'class': 'form-control'}),
            'to_status': forms.Select(attrs={'class': 'form-control'}),
            'allowed_groups': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

