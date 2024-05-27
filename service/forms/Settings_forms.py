from django import forms
from service.models import Status, Priority, RequestType, PriorityDuration, StatusTransition
from colorfield.fields import ColorField, ColorWidget

class RequestTypeForm(forms.ModelForm):
    class Meta:
        model = RequestType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
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


class ColorInput(forms.widgets.Input):
    input_type = "color"


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name', 'color', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            'color': ColorWidget(attrs={'id': 'id_color'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите описание'}),
            
        }
        
        #color=forms.CharField(max_length=7,widget=forms.TextInput(attrs={"type": "color", }))

    def __init__(self, *args, **kwargs):
        super(StatusForm, self).__init__(*args, **kwargs)

class StatusTransitionForm(forms.ModelForm):
    class Meta:
        model = StatusTransition
        fields = ['from_status', 'to_status', 'allowed_groups']


