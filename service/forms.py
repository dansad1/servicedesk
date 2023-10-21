from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Priority
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
        fields = ['title', 'description', 'assignee', 'completed', 'status', 'request_type', 'due_date', 'priority']

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)

        # Заполните поле priority данными из базы данных
        self.fields['priority'] = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                                         widget=forms.Select(attrs={'class': 'form-control'}))

        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        self.fields['completed'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['status'] = forms.ModelChoiceField(queryset=Status.objects.all(), required=False)
        self.fields['request_type'] = forms.ModelChoiceField(queryset=RequestType.objects.all(), required=False)
        self.fields['due_date'].widget.attrs.update({'class': 'form-control datetimepicker-input'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': CKEditorWidget()}