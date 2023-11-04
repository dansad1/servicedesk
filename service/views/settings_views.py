# views.py
from django.shortcuts import render, redirect
from ..forms import RequestTypeForm
from ..models import RequestType

def create_request_type(request):
    if request.method == 'POST':
        form = RequestTypeForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a new URL:
            return redirect('types_list.html')
    else:
        form = RequestTypeForm()
    return render(request, 'request_type.html', {'form': form})
def types_list(request):
    request_types = RequestType.objects.all()
    return render(request, 'types_list.html', {'types_list': request_types})

