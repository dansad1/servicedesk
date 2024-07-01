from service.forms.Request_forms import User
from service.models import FieldMeta, FieldAccess, Priority, Status, Company, CustomUser
from django import forms
from django.contrib.auth.models import Group


class FieldMetaForm(forms.ModelForm):
    class Meta:
        model = FieldMeta
        fields = ['name', 'field_type', 'is_required', 'show_name', 'unit', 'hint']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_name': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'hint': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(FieldMetaForm, self).__init__(*args, **kwargs)
        field_type = self.initial.get('field_type', self.instance.field_type if self.instance else None)
        self.fields['default_value'] = self.get_default_value_field(field_type)
        self.fields['default_value'].widget.attrs.update({'class': 'form-control'})

    def get_default_value_field(self, field_type):
        if field_type == 'text':
            return forms.CharField(label="Значение по умолчанию", required=False, widget=forms.TextInput())
        elif field_type == 'textarea':
            return forms.CharField(label="Значение по умолчанию", required=False, widget=forms.Textarea())
        elif field_type == 'date':
            return forms.DateField(label="Значение по умолчанию", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
        elif field_type == 'file':
            return forms.FileField(label="Значение по умолчанию", required=False, widget=forms.ClearableFileInput())
        elif field_type == 'number':
            return forms.FloatField(label="Значение по умолчанию", required=False, widget=forms.NumberInput())
        elif field_type == 'boolean':
            return forms.BooleanField(label="Значение по умолчанию", required=False, widget=forms.CheckboxInput())
        elif field_type == 'email':
            return forms.EmailField(label="Значение по умолчанию", required=False, widget=forms.EmailInput())
        elif field_type == 'url':
            return forms.URLField(label="Значение по умолчанию", required=False, widget=forms.URLInput())
        elif field_type == 'json':
            return forms.JSONField(label="Значение по умолчанию", required=False, widget=forms.Textarea())
        elif field_type == 'status':
            return forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=Status.objects.all(), widget=forms.Select())
        elif field_type == 'company':
            return forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=Company.objects.all(), widget=forms.Select())
        elif field_type == 'priority':
            return forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=Priority.objects.all(), widget=forms.Select())
        elif field_type == 'requester':
            return forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=CustomUser.objects.all(), widget=forms.Select())
        elif field_type == 'assignee':
            return forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=CustomUser.objects.all(), widget=forms.Select())
        else:
            return forms.CharField(label="Значение по умолчанию", required=False, widget=forms.TextInput())

class FieldAccessForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Group.objects.all(), required=True,
                                  widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = FieldAccess
        fields = ['role', 'field_meta', 'can_read', 'can_update']
        widgets = {
            'can_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_update': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


FieldAccessFormSet = forms.inlineformset_factory(FieldMeta, FieldAccess, form=FieldAccessForm, extra=0, can_delete=True)
