from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from service.models import CustomUser, Company,Request,Status,Request_type
from service.forms import  CompanyForm
from django.contrib.auth import login
from service.forms import CustomUserCreationForm
from django.urls import reverse_lazy
from  service.forms import *
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required,user_passes_test
from service.permissions import*
from django.contrib.auth.models import Group



@login_required
def request_list(request):
    user = request.user
    if is_in_group(user, "Администратор"):
        requests = Request.objects.all()
    else:
        requests = Request.objects.filter(company=user.company)
    context = {'requests': requests}
    return render(request, 'request/request_list.html', context)
@login_required
def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.requester = request.user

            # Check if the "Открыта" status exists; if not, create it
            status, created = Status.objects.get_or_create(name='Открыта')
            new_request.status = status

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
    can_edit = can_edit_request(user, request_instance)
    can_change_status = can_edit or user == request_instance.assignee

    if can_edit:
        if request.method == 'POST':
            form = RequestForm(request.POST, instance=request_instance)
            comment_form = CommentForm(request.POST)
            if form.is_valid() and comment_form.is_valid():
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

                # Save the new comment
                new_comment = comment_form.save(commit=False)
                new_comment.request = request_instance
                new_comment.author = request.user
                new_comment.save()

                return redirect('request_detail', pk=pk)
        else:
            form = RequestForm(instance=request_instance)
            comment_form = CommentForm()

        comments = Comment.objects.filter(request=request_instance)

        return render(request, 'request/request_update.html', {
            'form': form,
            'request_instance': request_instance,
            'comment_form': comment_form,
            'comments': comments,
        })
    else:
        messages.error(request, 'У вас нет разрешения на редактирование этой заявки.')
        return redirect('request_detail', pk=pk)
