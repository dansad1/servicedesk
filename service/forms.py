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
    status = forms.ModelChoiceField(queryset=Status.objects.all(), empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Request
        fields = ['title', 'description', 'status']