from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Priority, SavedFilter
from .models import Company,Request,Status,Comment,RequestType,Department,PriorityDuration,StatusTransition
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.widgets import CKEditorWidget

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address','company','role')

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'description']  # Здесь перечислите поля, которые вы хотите отображать в форме
class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'assignee', 'status', 'request_type', 'due_date', 'priority']

    duration_in_hours = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        # Expecting 'current_status' to be passed as a keyword argument
        current_status = kwargs.pop('current_status', None)
        super(RequestForm, self).__init__(*args, **kwargs)

        self.fields['priority'].widget.attrs.update({'class': 'form-control'})
        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['request_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['due_date'].widget.attrs.update({'class': 'form-control datetimepicker-input'})

        # If 'current_status' is provided, filter the 'status' field queryset accordingly
        if current_status:
            valid_next_statuses = StatusTransition.objects.filter(
                from_status=current_status
            ).values_list('to_status', flat=True)
            self.fields['status'].queryset = Status.objects.filter(id__in=valid_next_statuses)
        else:
            self.fields['status'].queryset = Status.objects.none()  # No status should be selectable by default

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': CKEditorWidget()}

class RequestFilterForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    filter_name = forms.CharField(max_length=100, required=False)
    requester = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    assignee = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    company = forms.ModelMultipleChoiceField(queryset=Company.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    status = forms.ModelMultipleChoiceField(queryset=Status.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    created_at = forms.DateTimeField(required=False)
    updated_at = forms.DateTimeField(required=False)
    priority = forms.ModelMultipleChoiceField(queryset=Priority.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    request_type = forms.ModelMultipleChoiceField(queryset=RequestType.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)


class SavedFilterForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        fields = ['filter_name', 'filter_data']

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
class RequestTypeForm(forms.ModelForm):
    class Meta:
        model = RequestType
        fields = ['name', 'description']
class PriorityForm(forms.ModelForm):
    class Meta:
        model = Priority
        fields = ['name']
class PriorityDurationForm(forms.ModelForm):
    class Meta:
        model = PriorityDuration
        fields = ['request_type', 'priority', 'duration_in_hours']
class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name', 'color', 'description']

class StatusTransitionForm(forms.ModelForm):
    class Meta:
        model = StatusTransition
        fields = ['from_status', 'to_status', 'allowed_groups']
