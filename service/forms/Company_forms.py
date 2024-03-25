from pytz import all_timezones

from service.models import CustomUser, Company, Department
from django import forms
from django.forms.widgets import CheckboxSelectMultiple

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'region', 'address', 'phone', 'email', 'website', 'description', 'ceo', 'deputy', 'contact_person', 'timezone']

    REGION_CHOICES = [
        ('spb', 'Санкт-Петербург'),
        ('moscow', 'Москва')
    ]
    region = forms.ChoiceField(choices=REGION_CHOICES, label='Регион')

    def __init__(self, *args, **kwargs):
        company_id = kwargs.pop('company_id', None)  # Извлекаем company_id из аргументов
        super(CompanyForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        if company_id:
            employees_queryset = CustomUser.objects.filter(company_id=company_id)
            self.fields['ceo'].queryset = employees_queryset
            self.fields['deputy'].queryset = employees_queryset
            self.fields['contact_person'].queryset = employees_queryset

        self.fields['timezone'].widget = forms.Select(choices=[(tz, tz) for tz in all_timezones],
                                                      attrs={'class': 'form-control'})


class DepartmentForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),  # Начальный пустой queryset, который будет задан динамически
        widget=CheckboxSelectMultiple,
        required=False  # Сделать выбор пользователей необязательным
    )

    class Meta:
        model = Department
        fields = ['name', 'parent', 'company', 'users']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.HiddenInput(),
            # 'users': уже определено выше
        }

    def __init__(self, *args, **kwargs):
        company_id = kwargs.pop('company_id', None)
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Department.objects.none()

        if company_id:
            self.fields['parent'].queryset = Department.objects.filter(company_id=company_id)
            self.fields['users'].queryset = CustomUser.objects.filter(company_id=company_id)  # Фильтрация пользователей по компании
