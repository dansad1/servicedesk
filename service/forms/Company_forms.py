from pytz import all_timezones

from service.models import CustomUser, Company, Department, CompanyFieldMeta, CompanyFieldSet, CompanyFieldValue, \
    CompanyCustomField
from django import forms
from django.forms.widgets import CheckboxSelectMultiple



class DepartmentForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),  # Изменится далее
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Department
        fields = ['name', 'parent', 'company', 'users']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.HiddenInput(),  # Компания устанавливается скрытым полем
        }

    def __init__(self, *args, **kwargs):
        company_id = kwargs.pop('company_id', None)
        super(DepartmentForm, self).__init__(*args, **kwargs)
        if company_id:
            self.fields['parent'].queryset = Department.objects.filter(company_id=company_id)
            # Это место нужно исправить для правильной фильтрации пользователей
            self.fields['users'].queryset = CustomUser.objects.filter(company_id=company_id)
class CompanyFieldMetaForm(forms.ModelForm):
    class Meta:
        model = CompanyFieldMeta
        fields = ['name', 'field_type', 'is_required']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CompanyFieldValueForm(forms.ModelForm):
    class Meta:
        model = CompanyFieldValue
        fields = [
            'value_text', 'value_number', 'value_date', 'value_boolean',
            'value_email', 'value_url', 'value_json', 'value_file',
            #'value_phone'
        ]
        widgets = {
            'value_text': forms.TextInput(attrs={'class': 'form-control'}),
            'value_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'value_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'value_boolean': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'value_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'value_url': forms.URLInput(attrs={'class': 'form-control'}),
            'value_json': forms.Textarea(attrs={'class': 'form-control'}),
            'value_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            #'value_phone': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),  # Виджет для телефона
        }

    def __init__(self, *args, **kwargs):
        field_meta = kwargs.pop('field_meta', None)
        super().__init__(*args, **kwargs)
        if field_meta:
            self.fields['value_text'].label = field_meta.name
            self.fields['value_number'].label = field_meta.name
            self.fields['value_date'].label = field_meta.name
            self.fields['value_boolean'].label = field_meta.name
            self.fields['value_email'].label = field_meta.name
            self.fields['value_url'].label = field_meta.name
            self.fields['value_json'].label = field_meta.name
            self.fields['value_file'].label = field_meta.name
          #  self.fields['value_phone'].label = field_meta.name
class CompanyCustomFieldForm(forms.ModelForm):
    class Meta:
        model = CompanyCustomField
        fields = ['name', 'field_type', 'value_text', 'value_number', 'value_date', 'value_boolean', 'value_email', 'value_url', 'value_json', 'value_file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'value_text': forms.TextInput(attrs={'class': 'form-control'}),
            'value_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'value_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'value_boolean': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'value_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'value_url': forms.URLInput(attrs={'class': 'form-control'}),
            'value_json': forms.Textarea(attrs={'class': 'form-control'}),
            'value_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['value_text'].label = "Значение (Text)"
        self.fields['value_number'].label = "Значение (Number)"
        self.fields['value_date'].label = "Значение (Date)"
        self.fields['value_boolean'].label = "Значение (Boolean)"
        self.fields['value_email'].label = "Значение (Email)"
        self.fields['value_url'].label = "Значение (URL)"
        self.fields['value_json'].label = "Значение (JSON)"
        self.fields['value_file'].label = "Значение (File)"


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name']  # Поле 'name' оставляем статическим
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        # Получаем скрытые поля компании
        hidden_fields = company.hidden_fields.all() if company else CompanyFieldMeta.objects.none()

        # Добавляем стандартные поля компании в форму
        for field_meta in CompanyFieldMeta.objects.all():
            field_name = f'field_{field_meta.id}'
            initial_value = None
            if self.instance.pk:
                try:
                    field_value = CompanyFieldValue.objects.get(company=self.instance, company_field_meta=field_meta)
                    initial_value = field_value.get_value()
                except CompanyFieldValue.DoesNotExist:
                    pass

            self.fields[field_name] = self.get_form_field(field_meta, initial_value)

            # Добавляем checkbox для управления видимостью этого поля
            visible_field_name = f'visible_{field_meta.id}'
            self.fields[visible_field_name] = forms.BooleanField(
                required=False,
                initial=(field_meta not in hidden_fields),
                label=f"Показать поле: {field_meta.name}"
            )

    def get_form_field(self, field_meta, initial_value=None):
        field_class = {
            'text': forms.CharField,
            'textarea': forms.CharField,
            'number': forms.FloatField,
            'date': forms.DateField,
            'boolean': forms.BooleanField,
            'email': forms.EmailField,
            'url': forms.URLField,
            'json': forms.JSONField,
            'file': forms.FileField,
        }.get(field_meta.field_type, forms.CharField)

        widget = self.get_widget(field_meta)
        return field_class(
            label=field_meta.name,
            required=field_meta.is_required,
            initial=initial_value,
            widget=widget
        )

    def get_widget(self, field_meta):
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'textarea': forms.Textarea(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'boolean': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'json': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        return widgets.get(field_meta.field_type, forms.TextInput(attrs={'class': 'form-control'}))

    def save(self, commit=True):
        company = super().save(commit=False)

        if commit:
            company.save()

            # Сохраняем значения динамических полей
            for field_meta in CompanyFieldMeta.objects.all():
                field_name = f'field_{field_meta.id}'
                value = self.cleaned_data.get(field_name)

                # Определяем правильное имя поля в зависимости от типа
                field_type_map = {
                    'text': 'value_text',
                    'textarea': 'value_text',
                    'number': 'value_number',
                    'date': 'value_date',
                    'boolean': 'value_boolean',
                    'email': 'value_email',
                    'url': 'value_url',
                    'json': 'value_json',
                    'file': 'value_file',
                }
                field_name_to_update = field_type_map.get(field_meta.field_type)

                # Обновляем или создаем значение поля
                CompanyFieldValue.objects.update_or_create(
                    company=company,
                    company_field_meta=field_meta,
                    defaults={field_name_to_update: value}
                )

            # Обновляем видимость полей
            hidden_fields = []
            for field_meta in CompanyFieldMeta.objects.all():
                visible_field_name = f'visible_{field_meta.id}'
                if not self.cleaned_data.get(visible_field_name):
                    hidden_fields.append(field_meta)

            company.hidden_fields.set(hidden_fields)
            company.save()

        return company
