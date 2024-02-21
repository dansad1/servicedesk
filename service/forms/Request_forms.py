from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth import get_user_model
from django.forms import SelectMultiple, DateInput
from service.models import StatusTransition, Status, Comment, Request, Company, Priority, RequestType, SavedFilter

User = get_user_model()


class RequestForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    duration_in_hours = forms.IntegerField(required=False, widget=forms.HiddenInput())
    attachment = forms.FileField(required=False)
    request_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Request
        # Исключаем 'request_type' из списка отображаемых полей
        fields = ['title', 'description', 'assignee', 'status', 'due_date', 'priority']

    def __init__(self, *args, **kwargs):
        current_status = kwargs.pop('current_status', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        # Styling for fields
        for field_name in ['priority', 'assignee', 'status', 'due_date']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})
        self.fields['due_date'].widget.attrs.update({'class': 'form_control datetimepicker-input'})

        # Make status field optional and set initial values
        self.fields['status'].required = False
        self.fields['status'].empty_label = "No change"

        # Adjust status field based on current status
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
    title = forms.CharField(max_length=100, required=False)
    filter_name = forms.CharField(max_length=100, required=False)

    requester = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    assignee = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    company = forms.ModelMultipleChoiceField(
        queryset=Company.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    status = forms.ModelMultipleChoiceField(
        queryset=Status.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    created_at = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )

    updated_at = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        required=False
    )

    priority = forms.ModelMultipleChoiceField(
        queryset=Priority.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )

    request_type = forms.ModelMultipleChoiceField(
        queryset=RequestType.objects.all(),
        widget=SelectMultiple(attrs={'class': 'select2'}),
        required=False
    )
class SavedFilterForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        fields = ['filter_name', 'filter_data']
