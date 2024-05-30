from django.shortcuts import render, redirect
from service.forms.Chat_forms import MessageForm
from service.models import ChatMessage
import json
import requests as r


def get_response(response: str):
    url = "http://rag-pipeline:8085/rag_router/rag_final_response"
    data = {
        "text": 'sads',
        "encoding_model": "gigachat",
        "n_results": 10,
        "include_embeddings": "false"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = r.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data[0]
    else:
        return "Error: bad connection "



def chat_view(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.user = request.user
            chat_message.save()

            chat_message1 = ChatMessage()
            chat_message1.user = request.user
            chat_message1.message = get_response(chat_message.message)
            chat_message1.save()

            return redirect('chat_view')
    else:
        form = MessageForm()
    messages = ChatMessage.objects.all().order_by('-timestamp')
    return render(request, 'chat/chat.html', {'form': form, 'messages': messages})
