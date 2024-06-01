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
        super().__init__(*args, **kwargs)
        for permission in self.fields['custompermission'].queryset:
            
            field_name = f'access_level_{permission.id}'
            self.fields[field_name] = forms.ChoiceField(
                choices=GroupPermission.ACCESS_LEVEL_CHOICES,
                initial='personal',  # Установите здесь значение по умолчанию
                widget=forms.RadioSelect,
                label=f"Уровень доступа для {permission.code_name}"
            )
            
        requests_2_permissions = self.fields['custompermission'].queryset.filter(code_name="requests_2")
         # Получить значения id для каждого custompermission с code_name "requests_2"
        requests_2_permission_ids = list(requests_2_permissions.values_list('id', flat=True))
        # Установить эти id в качестве значений по умолчанию для поля custompermission
        self.initial['custompermission'] = requests_2_permission_ids
    
    
    
    class Meta:
        model = GroupPermission
        fields = ['group', 'custompermission']
        