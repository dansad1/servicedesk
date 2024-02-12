from pytz import all_timezones

from service.models import CustomUser, Company, Department
from django import forms

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
    class Meta:
        model = Department
        fields = ['name']
