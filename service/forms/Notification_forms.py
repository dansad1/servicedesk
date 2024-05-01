from django import forms
from service.models import NotificationSetting

class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ['email_template']
        widgets = {
            'email_template': forms.Textarea(attrs={'cols': 40, 'rows': 4})
        }
