from django import forms
from service.models import ChatMessage, Doc


class MessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type your message here...'})
        }


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Doc
        fields = ('title', 'doc_file',)
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок документа'}),
            'doc_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
