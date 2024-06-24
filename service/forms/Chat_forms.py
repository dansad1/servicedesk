from django import forms
from service.models import ChatMessage, Doc


class MessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type your message here...'})
        }



