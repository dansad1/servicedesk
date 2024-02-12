from django import forms
from django.contrib.auth.models import Group

from service.models import CustomPermission


class GroupForm(forms.ModelForm):
    action_permissions = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.filter(code_name__startswith='action_'),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Разрешения Действий'
    )
    section_permissions = forms.ModelMultipleChoiceField(
        queryset=CustomPermission.objects.filter(code_name__startswith='section_'),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Разрешения для Разделов'
    )

    class Meta:
        model = Group
        fields = ['name']

    def __init__(self, *args, **kwargs):
        group = kwargs.get('instance')
        super(GroupForm, self).__init__(*args, **kwargs)

        # Инициализация начальных значений для разрешений действий
        if group:
            self.initial['action_permissions'] = group.grouppermission_set.filter(
                custompermission__code_name__startswith='action_'
            ).values_list('custompermission__id', flat=True)
            # Инициализация начальных значений для разрешений разделов
            self.initial['section_permissions'] = group.grouppermission_set.filter(
                custompermission__code_name__startswith='section_'
            ).values_list('custompermission__id', flat=True)

        # Добавляем динамические поля для уровней доступа
        for permission in CustomPermission.objects.filter(code_name__startswith='action_'):
            field_name = f'access_level_{permission.id}'
            self.fields[field_name] = forms.ChoiceField(
                choices=[('global', 'Global'), ('company', 'Company'), ('department', 'Department'), ('personal', 'Personal')],
                required=False,
                label='Уровень доступа для ' + permission.name
            )
            # Установка начального значения для уровня доступа, если группа уже имеет это разрешение
            if group:
                access_level = group.grouppermission_set.filter(custompermission=permission).first()
                if access_level:
                    self.initial[field_name] = access_level.access_level