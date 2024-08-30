from pytz import all_timezones

from service.models import CustomUser, Company, Department, CompanyFieldMeta, CompanyFieldSet, CompanyFieldValue, \
    CompanyCustomFieldValue, CompanyCustomFieldMeta
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
class CompanyCustomFieldMetaForm(forms.ModelForm):
    class Meta:
        model = CompanyCustomFieldMeta
        fields = ['name', 'field_type', 'is_required']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields['name'].label = f"Название кастомного поля для {company.name}"
class CompanyCustomFieldValueForm(forms.ModelForm):
    class Meta:
        model = CompanyCustomFieldValue  # Исправлено: используем правильную модель
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
            # Устанавливаем метки полей в зависимости от метаданных
            self.fields['value_text'].label = field_meta.name
            self.fields['value_number'].label = field_meta.name
            self.fields['value_date'].label = field_meta.name
            self.fields['value_boolean'].label = field_meta.name
            self.fields['value_email'].label = field_meta.name
            self.fields['value_url'].label = field_meta.name
            self.fields['value_json'].label = field_meta.name
            self.fields['value_file'].label = field_meta.name
          #  self.fields['value_phone'].label = field_meta.name

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
            if field_meta not in hidden_fields:
                field_name = f'field_{field_meta.id}'
                initial_value = self.get_initial_field_value(company, field_meta)
                self.fields[field_name] = self.get_form_field(field_meta, initial_value)

        # Добавляем кастомные поля компании в форму
        if company:
            for custom_field_meta in company.custom_field_meta.all():
                field_name = f'custom_field_{custom_field_meta.id}'
                initial_value = self.get_initial_custom_field_value(company, custom_field_meta)
                self.fields[field_name] = self.get_form_field(custom_field_meta, initial_value)

    def get_initial_field_value(self, company, field_meta):
        """
        Получает начальное значение для стандартного поля на основе данных компании.
        """
        if company:
            try:
                field_value = CompanyFieldValue.objects.get(company=company, company_field_meta=field_meta)
                return field_value.get_value()
            except CompanyFieldValue.DoesNotExist:
                return None
        return None

    def get_initial_custom_field_value(self, company, custom_field_meta):
        """
        Получает начальное значение для кастомного поля на основе данных компании.
        """
        if company:
            try:
                custom_field_value = CompanyCustomFieldValue.objects.get(company=company, custom_field_meta=custom_field_meta)
                return custom_field_value.get_value()
            except CompanyCustomFieldValue.DoesNotExist:
                return None
        return None

    def get_form_field(self, field_meta, initial_value=None):
        """
        Генерирует поле формы в зависимости от типа метаданных поля.
        """
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
        """
        Возвращает соответствующий виджет для типа поля.
        """
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

            # Сохраняем значения стандартных полей
            for field_meta in CompanyFieldMeta.objects.all():
                field_name = f'field_{field_meta.id}'
                value = self.cleaned_data.get(field_name)

                if value is not None:  # Проверяем, что значение не пустое
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

                    if field_name_to_update:  # Добавляем проверку
                        CompanyFieldValue.objects.update_or_create(
                            company=company,
                            company_field_meta=field_meta,
                            defaults={field_name_to_update: value}
                        )

            # Сохраняем значения кастомных полей
            for custom_field_meta in company.custom_field_meta.all():
                field_name = f'custom_field_{custom_field_meta.id}'
                value = self.cleaned_data.get(field_name)

                if value is not None:  # Проверяем, что значение не пустое
                    field_name_to_update = field_type_map.get(custom_field_meta.field_type)

                    if field_name_to_update:  # Добавляем проверку
                        CompanyCustomFieldValue.objects.update_or_create(
                            company=company,
                            custom_field_meta=custom_field_meta,
                            defaults={field_name_to_update: value}
                        )
        return company


class FieldVisibilityForm(forms.Form):
    """
    Форма для управления видимостью полей компании.
    Генерирует динамические поля-чекбоксы для каждого метаданных поля.
    """
    def __init__(self, *args, **kwargs):
        # Получаем компанию из дополнительных аргументов
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        # Если компания передана, создаем поля-чекбоксы для стандартных полей
        if company:
            for field_meta in CompanyFieldMeta.objects.all():
                field_name = f'visible_{field_meta.id}'
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    initial=(field_meta not in company.hidden_fields.all()),
                    label=field_meta.name
                )

            # Создаем поля-чекбоксы для кастомных полей
            for custom_field_meta in company.custom_field_meta.all():
                custom_field_name = f'visible_custom_{custom_field_meta.id}'
                self.fields[custom_field_name] = forms.BooleanField(
                    required=False,
                    initial=(custom_field_meta not in company.hidden_custom_fields.all()),
                    label=custom_field_meta.name
                )
