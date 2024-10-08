from service.forms.Request_forms import User
from service.models import RequestFieldMeta, RequestFieldAccess, Priority, Status, Company, CustomUser
from django import forms
from django.contrib.auth.models import Group

class FieldMetaForm(forms.ModelForm):
    class Meta:
        model = RequestFieldMeta
        fields = ['name', 'field_type', 'is_required', 'show_name', 'unit', 'hint', 'default_value']
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
        field_type_mapping = {
            'text': forms.CharField(label="Значение по умолчанию", required=False, widget=forms.TextInput()),
            'textarea': forms.CharField(label="Значение по умолчанию", required=False, widget=forms.Textarea()),
            'date': forms.DateField(label="Значение по умолчанию", required=False, widget=forms.DateInput(attrs={'type': 'date'})),
            'file': forms.FileField(label="Значение по умолчанию", required=False, widget=forms.ClearableFileInput()),
            'number': forms.FloatField(label="Значение по умолчанию", required=False, widget=forms.NumberInput()),
            'boolean': forms.BooleanField(label="Значение по умолчанию", required=False, widget=forms.CheckboxInput()),
            'email': forms.EmailField(label="Значение по умолчанию", required=False, widget=forms.EmailInput()),
            'url': forms.URLField(label="Значение по умолчанию", required=False, widget=forms.URLInput()),
            'json': forms.JSONField(label="Значение по умолчанию", required=False, widget=forms.Textarea()),
            'status': forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=Status.objects.all(), widget=forms.Select()),
            'company': forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=Company.objects.all(), widget=forms.Select()),
            'priority': forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=Priority.objects.all(), widget=forms.Select()),
            'requester': forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=CustomUser.objects.all(), widget=forms.Select()),
            'assignee': forms.ModelChoiceField(label="Значение по умолчанию", required=False, queryset=CustomUser.objects.all(), widget=forms.Select())
        }
        return field_type_mapping.get(field_type, forms.CharField(label="Значение по умолчанию", required=False, widget=forms.TextInput()))

    def clean_default_value(self):
        default_value = self.cleaned_data.get('default_value')
        field_type = self.cleaned_data.get('field_type')

        if field_type in ['status', 'company', 'priority', 'requester', 'assignee'] and default_value:
            return default_value.id
        return default_value

    def save(self, commit=True):
        instance = super(FieldMetaForm, self).save(commit=False)
        default_value_field = self.cleaned_data.get('default_value')
        if default_value_field is not None:
            if isinstance(default_value_field, (Status, Company, Priority, CustomUser)):
                instance.default_value = default_value_field.id
            else:
                instance.default_value = default_value_field
        if commit:
            instance.save()
        return instance

class FieldAccessForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = RequestFieldAccess
        fields = ['role', 'can_read', 'can_update']
        widgets = {
            'can_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_update': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }