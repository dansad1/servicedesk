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
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название роли'
            })
        }

class GroupPermissionForm(forms.ModelForm):
    custompermission = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Полномочия"
    )

    def __init__(self, *args, **kwargs):
        group = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if group:
            group_permissions = GroupPermission.objects.filter(group=group)
            self.initial['custompermission'] = [gp.custompermission.id for gp in group_permissions]

            for permission in self.fields['custompermission'].queryset:
                field_name = f'access_level_{permission.id}'
                self.fields[field_name] = forms.ChoiceField(
                    choices=GroupPermission._meta.get_field('access_level').choices,
                    widget=forms.RadioSelect,
                    required=False,
                    label=f"Уровень доступа для {permission.name}"
                )

                for gp in group_permissions:
                    if gp.custompermission.id == permission.id:
                        self.initial[field_name] = gp.access_level

    class Meta:
        model = GroupPermission
        fields = ['custompermission']
