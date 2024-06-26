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


class FieldMetaForm(forms.ModelForm):
    class Meta:
        model = FieldMeta
        fields = ['name', 'field_type', 'is_required', 'show_name', 'default_value', 'unit', 'hint']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_name': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'default_value': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'hint': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FieldAccessForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Group.objects.all(), required=True,
                                  widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = FieldAccess
        fields = ['role', 'field_meta', 'can_read', 'can_update']
        widgets = {
            'can_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_update': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


FieldAccessFormSet = forms.inlineformset_factory(FieldMeta, FieldAccess, form=FieldAccessForm, extra=1, can_delete=True)


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['request_type']  # Добавьте другие статические поля, если необходимо

    def __init__(self, *args, **kwargs):
        request_type = kwargs.pop('request_type', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        if request_type:
            for field_meta in request_type.field_set.fields.all():
                self.add_custom_field(field_meta)

    def add_custom_field(self, field_meta):
        field_name = f'custom_field_{field_meta.id}'
        if field_meta.field_type == 'text':
            self.fields[field_name] = forms.CharField(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=field_meta.default_value,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
        elif field_meta.field_type == 'textarea':
            self.fields[field_name] = forms.CharField(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=field_meta.default_value,
                widget=forms.Textarea(attrs={'class': 'form-control'})
            )
        elif field_meta.field_type == 'date':
            self.fields[field_name] = forms.DateField(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=field_meta.default_value,
                widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
            )
        elif field_meta.field_type == 'file':
            self.fields[field_name] = forms.FileField(
                label=field_meta.name,
                required=field_meta.is_required,
                widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
            )
        elif field_meta.field_type == 'number':
            self.fields[field_name] = forms.FloatField(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=field_meta.default_value,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
        elif field_meta.field_type == 'boolean':
            self.fields[field_name] = forms.BooleanField(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=field_meta.default_value,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
            )
        elif field_meta.field_type == 'email':
            self.fields[field_name] = forms.EmailField(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=field_meta.default_value,
                widget=forms.EmailInput(attrs={'class': 'form-control'})
            )
        elif field_meta.field_type == 'url':
            self.fields[field_name] = forms.URLField(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=field_meta.default_value,
                widget=forms.URLInput(attrs={'class': 'form-control'})
            )
        elif field_meta.field_type == 'json':
            self.fields[field_name] = forms.JSONField(
                label=field_meta.name,
                required=field_meta.is_required,
                initial=field_meta.default_value,
                widget=forms.Textarea(attrs={'class': 'form-control'})
            )
        elif field_meta.field_type == 'select':
            # Пример, если у вас есть предопределенные варианты
            self.fields[field_name] = forms.ChoiceField(
                label=field_meta.name,
                required=field_meta.is_required,
                choices=[('option1', 'Option 1'), ('option2', 'Option 2')],
                widget=forms.Select(attrs={'class': 'form-control'})
            )