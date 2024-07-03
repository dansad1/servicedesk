from django import forms
from django.contrib.auth.models import Group

from service.models import CustomPermission
from service.models import GroupPermission
from django.forms import TextInput

from django import forms
from django.contrib.auth.models import Group

from service.models import CustomPermission
from service.models import GroupPermission
from django.forms import TextInput


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название роли'})
        }

class GroupPermissionForm(forms.ModelForm):
    custompermission = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Полномочия"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for permission in self.fields['custompermission'].queryset:
            field_name = f'access_level_{permission.id}'
            self.fields[field_name] = forms.ChoiceField(
                choices=GroupPermission.ACCESS_LEVEL_CHOICES,
                initial='personal',
                widget=forms.RadioSelect,
                label=f"Уровень доступа для {permission.code_name}"
            )
        # Initialize the permissions
        if self.instance.pk:
            group_permissions = GroupPermission.objects.filter(group=self.instance)
            self.initial['custompermission'] = group_permissions.values_list('custompermission', flat=True)
            for permission in group_permissions:
                field_name = f'access_level_{permission.custompermission.id}'
                self.initial[field_name] = permission.access_level

    class Meta:
        model = GroupPermission
        fields = ['group', 'custompermission']