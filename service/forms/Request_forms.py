from datetime import timezone
from django.utils import timezone

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth import get_user_model
from django.forms import SelectMultiple, DateInput
from service.models import StatusTransition, Status, Comment, Request, Company, Priority, RequestType, SavedFilter, \
    FieldAccess, FieldMeta, FieldValue, CustomUser
from django.forms.widgets import Select
from django.contrib.auth.models import Group


User = get_user_model()





class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'attachment']  # Предполагается, что поля 'text' и 'attachment' определены в модели Comment
        widgets = {
            'text': CKEditorWidget(),  # Использует виджет CKEditor для поля 'text'
            # Для поля 'attachment' будет использоваться виджет по умолчанию, если не указано иное
        }

class RequestFilterForm(forms.Form):
    
    filter_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Название фильтра")

    requester = forms.ModelMultipleChoiceField(
        label="Заявитель",
        queryset=User.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2 form-control'}),
        required=False
    )

    assignee = forms.ModelMultipleChoiceField(
        label="Исполнитель",
        queryset=User.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2 form-control'}),
        required=False
    )

    company = forms.ModelMultipleChoiceField(
        label="Компания",
        queryset=Company.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2 form-control'}),
        required=False
    )

    status = forms.ModelMultipleChoiceField(
        label="Статус",
        queryset=Status.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2 form-control'}),
        required=False
    )

    created_at = forms.DateField(
        label="Дата создания",
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    updated_at = forms.DateField(
        label="Дата обновления",
        widget=DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    priority = forms.ModelMultipleChoiceField(
        label="Приоритет",
        queryset=Priority.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2 form-control'}),
        required=False
    )

    request_type = forms.ModelMultipleChoiceField(
        label="Тип заявки",
        queryset=RequestType.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2 form-control'}),
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        # Remove filter_name from cleaned_data to avoid using it in filters
        cleaned_data.pop('filter_name', None)
        return cleaned_data
    
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
    class Meta:
        model = Request
        fields = ['request_type']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        request_type = kwargs.pop('request_type', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        self.fields['request_type'].widget.attrs.update({'class': 'form-select'})

        if request_type:
            for field_meta in request_type.field_set.fields.all():
                field_name = f'custom_field_{field_meta.id}'
                initial_value = None
                if self.instance.pk:
                    try:
                        field_value = FieldValue.objects.get(request=self.instance, field_meta=field_meta)
                        initial_value = field_value.get_value()
                    except FieldValue.DoesNotExist:
                        pass
                else:
                    initial_value = self.get_initial_value(field_meta, user)
                field = self.get_form_field(field_meta, initial_value)
                field.widget.attrs['widget_class'] = field.widget.__class__.__name__
                self.fields[field_name] = field

    def get_form_field(self, field_meta, initial_value):
        field_class = {
            'text': forms.CharField,
            'textarea': forms.CharField,
            'date': forms.DateField,
            'file': forms.FileField,
            'number': forms.FloatField,
            'boolean': forms.BooleanField,
            'email': forms.EmailField,
            'url': forms.URLField,
            'json': forms.JSONField,
            'status': forms.ModelChoiceField,
            'company': forms.ModelChoiceField,
            'priority': forms.ModelChoiceField,
            'requester': forms.ModelChoiceField,
            'assignee': forms.ModelChoiceField,
        }.get(field_meta.field_type, forms.CharField)

        if field_meta.field_type in ['status', 'company', 'priority', 'requester', 'assignee']:
            queryset = self.get_queryset(field_meta.field_type)
            initial = field_meta.default_value if field_meta.field_type == 'status' and field_meta.default_value else initial_value
            return field_class(
                label=field_meta.name,
                required=field_meta.is_required,
                queryset=queryset,
                initial=initial,
                widget=forms.Select(attrs={'class': 'form-select'})
            )
        else:
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
            'textarea': forms.Textarea(attrs={'class': 'form-textarea'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'boolean': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'json': forms.Textarea(attrs={'class': 'form-textarea'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'requester': forms.Select(attrs={'class': 'form-select'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
        }
        return widgets.get(field_meta.field_type, forms.TextInput(attrs={'class': 'form-control'}))

    def get_queryset(self, field_type):
        querysets = {
            'status': Status.objects.all(),
            'company': Company.objects.all(),
            'priority': Priority.objects.all(),
            'requester': CustomUser.objects.all(),
            'assignee': CustomUser.objects.all(),
        }
        return querysets.get(field_type, CustomUser.objects.none())

    def get_initial_value(self, field_meta, user):
        if self.instance.pk:
            try:
                field_value = FieldValue.objects.get(request=self.instance, field_meta=field_meta)
                return field_value.get_value()
            except FieldValue.DoesNotExist:
                return None
        else:
            type_map = {
                'text': '',
                'textarea': '',
                'select': None,
                'number': 0,
                'date': timezone.now().date() if field_meta.name.lower() == 'due date' else None,
                'boolean': False,
                'email': user.email if field_meta.field_type == 'email' else '',
                'url': '',
                'json': {},
                'status': Status.objects.get(id=field_meta.default_value) if field_meta.default_value else None,
                'company': user.company if hasattr(user, 'company') else None,
                'priority': None,
                'requester': user if field_meta.field_type == 'requester' else None,
                'assignee': None,
                'request_type': None,
                'file': None,
            }
            return type_map.get(field_meta.field_type, '')

    def save(self, commit=True):
        instance = super(RequestForm, self).save(commit=False)
        if commit:
            instance.save()
            for field_name, field_value in self.cleaned_data.items():
                if field_name.startswith('custom_field_'):
                    field_id = int(field_name.split('_')[-1])
                    field_meta = FieldMeta.objects.get(id=field_id)
                    field_value_obj, created = FieldValue.objects.get_or_create(
                        request=instance,
                        field_meta=field_meta
                    )
                    field_value_obj.set_value(field_value)
                    field_value_obj.save()
        return instance