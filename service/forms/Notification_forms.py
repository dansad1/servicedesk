from ckeditor.widgets import CKEditorWidget
from django import forms
from service.models import NotificationSetting, NotificationTemplate


class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ['email_template']
        widgets = {
            'email_template': forms.Textarea(attrs={'cols': 40, 'rows': 4})
        }
class NotificationTemplateForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget(config_name='custom'))

    class Meta:
        model = NotificationTemplate
        fields = ['type', 'name', 'subject', 'body']