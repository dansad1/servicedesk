from django import forms

from service.models import EmailSettings


class EmailSettingsForm(forms.ModelForm):
    CONNECTION_CHOICES = [
        ('tls', 'TLS'),
        ('ssl', 'SSL'),
    ]

    connection_type = forms.ChoiceField(
        label="Использовать TLS или SSL",
        choices=CONNECTION_CHOICES,
        widget=forms.RadioSelect,
        initial='tls'
    )

    test_email_to = forms.EmailField(
        required=False,
        help_text="Введите адрес для тестового письма:",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@example.com'})
    )

    class Meta:
        model = EmailSettings
        fields = ['server', 'port', 'login', 'password', 'email_from', 'connection_type', 'test_email_to']
        widgets = {
            'server': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите сервер'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите порт'}),
            'login': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
            'email_from': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@example.com'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Здесь уже не нужно устанавливать use_tls и use_ssl напрямую, так как они определяются через connection_type
        if commit:
            instance.save()
        return instance
