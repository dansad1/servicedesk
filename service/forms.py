from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Company,Request,Status
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
        fields = ['title', 'description', 'assignee', 'completed']

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        self.fields['assignee'].widget.attrs.update({'class': 'form-control'})
        self.fields['completed'].widget.attrs.update({'class': 'form-check-input'})