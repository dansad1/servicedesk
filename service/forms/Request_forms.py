from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth import get_user_model
from django.forms import SelectMultiple, DateInput
from service.models import StatusTransition, Status, Comment, Request, Company, Priority, RequestType, SavedFilter
from django.forms.widgets import Select

User = get_user_model()


class RequestForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    duration_in_hours = forms.IntegerField(required=False, widget=forms.HiddenInput())
    attachment = forms.FileField(required=False)
    request_type = forms.ModelChoiceField(
        queryset=RequestType.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )
    
    class Meta:
        model = Request
        # Исключаем 'request_type' из списка отображаемых полей
        fields = ['title', 'description', 'assignee', 'status', 'due_date', 'priority']

    def __init__(self, *args, **kwargs):
        current_status = kwargs.pop('current_status', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        # Styling for fields
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget = Select(attrs={'class': 'form-control'})
        self.fields['due_date'].widget = DateInput(attrs={'class': 'form-control datetimepicker-input', 'type': 'date'})
        self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        
        self.fields['title'].label = "Название заявки:"
        self.fields['description'].label = "Описание заявки:"
        self.fields['assignee'].label = "Исполнитель:"
        self.fields['status'].label = "Статус:"
        self.fields['due_date'].label = "Срок выполнения:"
        self.fields['priority'].label = "Приоритет:"

        # Make status field optional and set initial values
        self.fields['status'].required = False
        self.fields['status'].empty_label = "No change"

        # Adjust status field based on current_status
        self.adjust_status_field(current_status)
    
    
    def adjust_status_field(self, current_status):
        if current_status:
            # Limit status choices to valid next statuses
            valid_next_statuses = StatusTransition.objects.filter(
                from_status=current_status
            ).values_list('to_status', flat=True)
            self.fields['status'].queryset = Status.objects.filter(
                id__in=valid_next_statuses
            ).union(Status.objects.filter(pk=current_status.pk))
            self.fields['status'].initial = current_status
        else:
            # Set a default status for new requests
            default_status, _ = Status.objects.get_or_create(name="Открыта")
            self.fields['status'].queryset = Status.objects.filter(pk=default_status.pk)
            self.fields['status'].initial = default_status

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'attachment']  # Предполагается, что поля 'text' и 'attachment' определены в модели Comment
        widgets = {
            'text': CKEditorWidget(),  # Использует виджет CKEditor для поля 'text'
            # Для поля 'attachment' будет использоваться виджет по умолчанию, если не указано иное
        }

class RequestFilterForm(forms.Form):
    title = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Заголовок")
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
    
    
class SavedFilterForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        fields = ['filter_name', 'filter_data']
