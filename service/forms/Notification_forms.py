from ckeditor.widgets import CKEditorWidget
from django import forms
from service.models import NotificationSetting, NotificationTemplate



class NotificationSettingForm(forms.ModelForm):
    email_template = forms.ModelChoiceField(queryset=NotificationTemplate.objects.filter(type='email'), required=False, widget=forms.Select())
    sms_template = forms.ModelChoiceField(queryset=NotificationTemplate.objects.filter(type='sms'), required=False, widget=forms.Select())
    push_template = forms.ModelChoiceField(queryset=NotificationTemplate.objects.filter(type='push'), required=False, widget=forms.Select())
    telegram_template = forms.ModelChoiceField(queryset=NotificationTemplate.objects.filter(type='telegram'), required=False, widget=forms.Select())
    whatsapp_template = forms.ModelChoiceField(queryset=NotificationTemplate.objects.filter(type='whatsapp'), required=False, widget=forms.Select())

    class Meta:
        model = NotificationSetting
        fields = ['email_template', 'sms_template', 'push_template', 'telegram_template', 'whatsapp_template']
class NotificationTemplateForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget(config_name='custom'))

    class Meta:
        model = NotificationTemplate
        fields = ['type', 'name', 'subject', 'body']