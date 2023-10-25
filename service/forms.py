from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Priority, SavedFilter
from .models import Company,Request,Status,Comment,RequestType
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
        super(RequestForm, self).__init__(*args, **kwargs)
        self.fields['priority'] = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                                         widget=forms.Select(attrs={'class': 'form-control'}))

        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'] = forms.ModelChoiceField(queryset=Status.objects.all(), required=False)
        self.fields['request_type'] = forms.ModelChoiceField(queryset=RequestType.objects.all(), required=True,
                                                             widget=forms.Select(attrs={'class': 'form-control'}))
        self.fields['due_date'].widget.attrs.update({'class': 'form-control datetimepicker-input'})

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
    completed = forms.NullBooleanField(required=False)
    created_at = forms.DateTimeField(required=False)
    updated_at = forms.DateTimeField(required=False)
    priority = forms.ModelMultipleChoiceField(queryset=Priority.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    request_type = forms.ModelMultipleChoiceField(queryset=RequestType.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)


class SavedFilterForm(forms.ModelForm):
    class Meta:
        model = SavedFilter
        fields = ['filter_name', 'filter_data']

