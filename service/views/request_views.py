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
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def request_list(request):
    user = request.user

    # Проверьте, может ли текущий пользователь видеть список заявок
    if user.is_superuser:
        # Если пользователь является администратором (superuser),
        # он видит все заявки
        requests = Request.objects.all()
    else:
        # Для всех остальных пользователей, ограничьте список заявок
        # заявками только их компании
        requests = Request.objects.filter(company=user.company)

    context = {
        'requests': requests,
    }
    return render(request, 'request/request_list.html', context)
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

    # Check if the user can edit the request
    can_edit = user.has_perm('change_request') or user == request_instance.requester

    # Check if the user can mark the request as completed
    can_mark_completed = can_edit or user.has_perm('change_request') or user == request_instance.assignee

    if can_edit and request.method == 'POST':
        form = RequestForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()
            # Update request status based on form data
            if request_instance.assignee:
                status_in_work, created = Status.objects.get_or_create(name="В работе")
                request_instance.status = status_in_work
            else:
                status_opened, created = Status.objects.get_or_create(name="Открыта")
                request_instance.status = status_opened

            is_completed = form.cleaned_data.get('completed', False)
            if is_completed:
                status_completed, created = Status.objects.get_or_create(name="Выполнена")
                request_instance.status = status_completed

            request_instance.save()
            return redirect('request_detail', pk=pk)
    else:
        form = RequestForm(instance=request_instance)

    context = {
        'request_instance': request_instance,
        'form': form,
        'can_edit': can_edit,
        'can_mark_completed': can_mark_completed,
    }

    return render(request, 'request/request_detail.html', context)
@login_required
def request_update(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    user = request.user

    # Check if the user can edit the request
    can_edit = user.has_perm('change_request') or user == request_instance.requester

    if can_edit and request.method == 'POST':
        form = RequestForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()
            # Update request status based on form data
            if request_instance.assignee:
                status_in_work, created = Status.objects.get_or_create(name="В работе")
                request_instance.status = status_in_work
            else:
                status_opened, created = Status.objects.get_or_create(name="Открыта")
                request_instance.status = status_opened

            is_completed = form.cleaned_data.get('completed', False)
            if is_completed:
                status_completed, created = Status.objects.get_or_create(name="Выполнена")
                request_instance.status = status_completed

            request_instance.save()
            return redirect('request_detail', pk=pk)
    else:
        form = RequestForm(instance=request_instance)

    context = {
        'request_instance': request_instance,
        'form': form,
        'can_edit': can_edit,
    }

    return render(request, 'request/request_update.html', context)