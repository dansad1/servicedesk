from datetime import timezone
from django.utils import timezone

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth import get_user_model
from django.forms import SelectMultiple, DateInput
from service.models import StatusTransition, Status, Comment, Request, Company, Priority, RequestType, SavedFilter,FieldAccess, FieldMeta
from django.forms.widgets import Select
from django.contrib.auth.models import Group


User = get_user_model()


#class RequestForm(forms.ModelForm):
 #   description = forms.CharField(widget=CKEditorWidget())
  #  duration_in_hours = forms.IntegerField(required=False, widget=forms.HiddenInput())
   # attachment = forms.FileField(required=False)
    #request_type = forms.ModelChoiceField(
    #    queryset=RequestType.objects.all(),
     #   widget=forms.HiddenInput(),
      #  required=False
    #)
    
    #class Meta:
     #   model = Request
        # Исключаем 'request_type' из списка отображаемых полей
        #fields = ['title', 'description', 'assignee', 'status', 'due_date', 'priority']

   # def __init__(self, *args, **kwargs):
    #    current_status = kwargs.pop('current_status', None)
        #super(RequestForm, self).__init__(*args, **kwargs)

        # Styling for fields
     #   self.fields['title'].widget.attrs.update({'class': 'form-control'})
      #  self.fields['description'].widget.attrs.update({'class': 'form-control'})
       # self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        #self.fields['status'].widget = Select(attrs={'class': 'form-control'})
        #self.fields['due_date'].widget = DateInput(attrs={'class': 'form-control datetimepicker-input', 'type': 'date'})
        #self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        
        #self.fields['title'].label = "Название заявки:"
        #self.fields['description'].label = "Описание заявки:"
        #self.fields['assignee'].label = "Исполнитель:"
        #self.fields['status'].label = "Статус:"
        #self.fields['due_date'].label = "Срок выполнения:"
        #self.fields['priority'].label = "Приоритет:"

        # Make status field optional and set initial values
      #  self.fields['status'].required = False
       # self.fields['status'].empty_label = "No change"

        # Adjust status field based on current_status
     #   self.adjust_status_field(current_status)
    
    
    #def adjust_status_field(self, current_status):
        #if current_status:
            # Limit status choices to valid next statuses
            #valid_next_statuses = StatusTransition.objects.filter(
             #   from_status=current_status
            #).values_list('to_status', flat=True)
           # self.fields['status'].queryset = Status.objects.filter(
          #      id__in=valid_next_statuses
         #   ).union(Status.objects.filter(pk=current_status.pk))
        #    self.fields['status'].initial = current_status
       # else:
            # Set a default status for new requests
           # default_status, _ = Status.objects.get_or_create(name="Открыта")
          #  self.fields['status'].queryset = Status.objects.filter(pk=default_status.pk)
         #   self.fields['status'].initial = default_status

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
        fields = ['request_type']  # Добавьте другие статические поля, если необходимо

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        request_type = kwargs.pop('request_type', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        if request_type:
            for field_meta in request_type.field_set.fields.all():
                self.fields[f'custom_field_{field_meta.id}'] = self.get_form_field(field_meta, user)

    def get_form_field(self, field_meta, user):
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
            initial_value = self.get_initial_value(field_meta, user)
            return field_class(label=field_meta.name, required=field_meta.is_required, queryset=queryset, initial=initial_value)
        else:
            initial_value = self.get_initial_value(field_meta, user)
            return field_class(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=initial_value,
                widget=self.get_widget(field_meta)
            )

    def get_widget(self, field_meta):
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'textarea': forms.Textarea(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'boolean': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'json': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'requester': forms.Select(attrs={'class': 'form-control'}),
            'assignee': forms.Select(attrs={'class': 'form-control'}),
        }
        return widgets.get(field_meta.field_type, forms.TextInput(attrs={'class': 'form-control'}))

    def get_queryset(self, field_type):
        querysets = {
            'status': Status.objects.all(),
            'company': Company.objects.all(),
            'priority': Priority.objects.all(),
            'requester': User.objects.all(),
            'assignee': User.objects.all(),
        }
        return querysets.get(field_type, User.objects.none())

    def get_initial_value(self, field_meta, user):
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
            'status': 'Открыта' if field_meta.field_type == 'status' else None,
            'company': user.company if field_meta.field_type == 'company' else None,
            'priority': None,
            'requester': user if field_meta.field_type == 'requester' else None,
            'assignee': None,
            'request_type': self.instance.request_type if field_meta.field_type == 'request_type' else None,
            'file': None,
        }
        return type_map.get(field_meta.field_type, '')