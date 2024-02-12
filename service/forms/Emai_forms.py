from django import forms

from service.models import EmailSettings


class EmailSettingsForm(forms.ModelForm):
    CONNECTION_CHOICES = [
        ('tls', 'TLS'),
        ('ssl', 'SSL'),
    ]

    connection_type = forms.ChoiceField(
        label="Use TLS or SSL",
        choices=CONNECTION_CHOICES,
        widget=forms.RadioSelect,
        initial='tls'
    )

    test_email_to = forms.EmailField(required=False, help_text="Введите адрес для тестового письма")
    class Meta:
     model = EmailSettings
     fields = ['server', 'port', 'login', 'password', 'email_from', 'connection_type']
     widgets = {
        'password': forms.PasswordInput(),  # Скрыть ввод пароля
    }

     def clean(self):
         cleaned_data = super().clean()
         connection_type = cleaned_data.get("connection_type")
         if connection_type == 'tls':
             cleaned_data['use_tls'] = True
             cleaned_data['use_ssl'] = False
         elif connection_type == 'ssl':
             cleaned_data['use_tls'] = False
             cleaned_data['use_ssl'] = True
         return cleaned_data