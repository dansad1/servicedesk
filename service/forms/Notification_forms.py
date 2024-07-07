from ckeditor.widgets import CKEditorWidget
from django import forms
from service.models import NotificationSetting, NotificationTemplate



class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ['template']
        widgets = {
            'template': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super(NotificationSettingForm, self).__init__(*args, **kwargs)
        self.fields['template'].queryset = NotificationTemplate.objects.all()
        self.fields['template'].required = False

class NotificationTemplateForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget(config_name='custom'))

    class Meta:
        model = NotificationTemplate
        fields = ['type', 'name', 'subject', 'body']