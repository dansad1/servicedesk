from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Company,Request
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address','company')

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company  # Используйте модель Company для создания формы
        fields = ['name', 'address', 'description']  # Укажите поля, которые вы хотите включить в форму

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'assignee']

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        # Добавьте необходимую логику для настройки полей формы, если требуется