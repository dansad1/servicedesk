from datetime import timezone, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth import get_user_model
from django.forms import SelectMultiple, DateInput
from service.models import StatusTransition, Status, Comment, Request, Company, Priority, RequestType, SavedFilter,RequestFieldAccess, RequestFieldMeta, RequestFiledValue, CustomUser, PriorityDuration
from django.forms.widgets import Select
from django.contrib.auth.models import Group

from service.utils.request_utils import add_dynamic_fields_to_form, save_custom_fields

User = get_user_model()

def generate_dynamic_form(fieldset, user=None):
    """
    Генерирует динамическую форму на основе FieldSet.
    """

    class DynamicRequestFilterForm(forms.Form):
        filter_name = forms.CharField(
            max_length=100,
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            label="Название фильтра"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Карта типов полей
            field_type_mapping = {
                'text': (forms.CharField, forms.TextInput),
                'textarea': (forms.CharField, forms.Textarea),
                'date': (forms.DateField, forms.DateInput),
                'file': (forms.FileField, forms.ClearableFileInput),
                'requester': (forms.ModelChoiceField, forms.Select, User.objects.filter(is_active=True)),
                'assignee': (forms.ModelChoiceField, forms.Select, User.objects.filter(is_active=True)),
                'company': (forms.ModelChoiceField, forms.Select, Company.objects.filter(users=user) if user else Company.objects.none()),
                'status': (forms.ModelChoiceField, forms.Select, Status.objects.all()),
                'priority': (forms.ModelChoiceField, forms.Select, Priority.objects.all()),
                'comment': (forms.CharField, forms.Textarea),
            }

            # Генерация полей
            for field in fieldset.fields.all():
                field_name = field.name.lower().replace(' ', '_')
                field_type = field_type_mapping.get(field.field_type)

                if not field_type:
                    continue  # Пропускаем неизвестные типы полей

                field_class = field_type[0]
                widget = field_type[1]
                queryset = field_type[2] if len(field_type) > 2 else None

                # Если поле требует queryset
                if queryset is not None:
                    self.fields[field_name] = field_class(
                        queryset=queryset,
                        required=False,
                        label=field.name,
                        widget=widget(attrs={'class': 'form-control'})
                    )
                else:  # Для остальных типов полей
                    self.fields[field_name] = field_class(
                        required=False,
                        label=field.name,
                        widget=widget(attrs={'class': 'form-control'})
                    )

        def clean(self):
            """
            Дополнительная очистка данных формы.
            """
            cleaned_data = super().clean()
            cleaned_data.pop('filter_name', None)  # Удаляем техническое поле
            return cleaned_data

    return DynamicRequestFilterForm


class SavedFilterForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        fields = ['filter_name', 'filter_data']

        widgets = {
            'filter_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название фильтра',
            }),
            'filter_data': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите данные фильтра',
                'rows': 5,
            }),
        }



class RequestForm(forms.ModelForm):
    """
    Форма для заявки с динамическими пользовательскими полями, зависящими от `request_type`.
    """

    def __init__(self, *args, user=None, **kwargs):
        # Извлекаем `initial` перед вызовом super()
        initial = kwargs.get('initial', {})
        self.user = user  # Сохраняем пользователя в атрибуте формы
        super().__init__(*args, **kwargs)

        # Получаем request_type из instance или initial
        self.request_type = self.instance.request_type if self.instance and self.instance.request_type else initial.get(
            'request_type')

        if not self.request_type:
            raise ValueError("Необходимо указать `request_type` для генерации пользовательских полей.")

        # Добавляем класс виджета для поля request_type
        self.fields['request_type'].widget.attrs.update({
            'class': 'form-select bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
        })

        # Добавляем динамические поля из FieldSet
        if self.request_type.field_set:
            add_dynamic_fields_to_form(self, self.request_type, self.user)

    def save(self, commit=True):
        """
        Сохраняет основную заявку и динамические пользовательские поля.
        """
        instance = super().save(commit=False)
        if commit:
            instance.save()  # Сохраняем основную заявку
            save_custom_fields(self.cleaned_data, instance, self.user)  # Сохраняем динамические поля
        return instance

    class Meta:
        model = Request
        fields = ['request_type']  # Статическое поле
