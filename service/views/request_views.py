from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from service.models import CustomUser, Company,Request,Status
from service.forms import  CompanyForm
from django.contrib.auth import login
from service.forms import CustomUserCreationForm
from django.urls import reverse_lazy
from  service.forms import *
from django.shortcuts import get_object_or_404
from django.urls import reverse
@login_required
def request_list(request):
    user = request.user
    requests = Request.objects.filter(company=user.company)
    return render(request, 'request/request_list.html', {'requests': requests, 'user': user})

@login_required
def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.requester = request.user
            new_request.status = Status.objects.get(name='Открыта')  # Set the default status to "Открыта"
            new_request.save()
            return redirect('request_list')
    else:
        form = RequestForm()

    return render(request, 'request/request_create.html', {'form': form})

@login_required
def request_detail(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    user = request.user

    # Check user roles to determine whether to redirect to update or detail view
    if user == request_instance.requester or user == request_instance.assignee or user.is_staff:
        url = reverse('request_update', args=[pk])
        return redirect(url)

    return render(request, 'request/request_detail.html', {'request_instance': request_instance})

@login_required
def request_update(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    user = request.user

    if request.method == 'POST':
        form = RequestForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()

            # Check if an assignee has been added to the request
            if request_instance.assignee:
                status_in_work, created = Status.objects.get_or_create(name="В работе")
                request_instance.status = status_in_work
            else:
                status_opened, created = Status.objects.get_or_create(name="Открыта")
                request_instance.status = status_opened

            # Check if the "completed" checkbox is checked
            is_completed = form.cleaned_data.get('completed', False)
            if is_completed:
                status_completed, created = Status.objects.get_or_create(name="Выполнена")
                request_instance.status = status_completed

            request_instance.save()

            return redirect('request_detail', pk=pk)
    else:
        form = RequestForm(instance=request_instance)

    return render(request, 'request/request_update.html', {'form': form, 'request_instance': request_instance})