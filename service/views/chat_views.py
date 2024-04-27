from django.shortcuts import render, redirect
from service.forms.Chat_forms import MessageForm
from service.models import ChatMessage


def chat_view(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.user = request.user
            chat_message.save()
            return redirect('chat_view')
    else:
        form = MessageForm()
    messages = ChatMessage.objects.all().order_by('-timestamp')
    return render(request, 'chat/chat.html', {'form': form, 'messages': messages})
