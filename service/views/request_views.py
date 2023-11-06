from django.core.checks import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from service.models import CustomUser, Company,Request,Status,RequestType
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
from django.utils import timezone
from service.models import *
from datetime import timedelta
from ..status_logic import *
from django.db.models import Q
from ..models import SavedFilter
from django.db.models import QuerySet
import json
from django.core.exceptions import ValidationError
import json

# Функция для обработки и применения фильтров
def handle_filters(request, initial_requests):
    load_filter_id = request.GET.get('load_filter')
    loaded_filters = {}
    if load_filter_id:
        try:
            saved_filter = SavedFilter.objects.get(id=load_filter_id, user=request.user)

            # Проверка типа filter_data
            if isinstance(saved_filter.filter_data, dict):
                loaded_filters = saved_filter.filter_data
            else:
                loaded_filters = json.loads(saved_filter.filter_data)  # предполагается, что это JSON-строка

            # Удаление ненужных ключей
            loaded_filters.pop('unknown', None)
            loaded_filters.pop('filter_name', None)

            initial_requests = apply_filters(initial_requests, loaded_filters)
        except (SavedFilter.DoesNotExist, json.JSONDecodeError):
            pass

    filter_form = RequestFilterForm(request.GET or None, initial=request.session.get('saved_filters', {}))

    if request.method == "GET" and filter_form.is_valid():
        filters = filter_form.cleaned_data
        filters.pop('filter_name', None)
        filtered_requests = apply_filters(initial_requests, filters)
    else:
        filtered_requests = initial_requests

    return filtered_requests, filter_form
# Основная функция для отображения списка заявок
def request_list(request):
    user = request.user

    if is_in_group(user, "Администратор"):
        initial_requests = Request.objects.all()
    else:
        initial_requests = Request.objects.filter(company=user.company)

    delete_filter_id = request.GET.get('delete_filter')
    if delete_filter_id:
        SavedFilter.objects.filter(id=delete_filter_id, user=user).delete()

    saved_filters = SavedFilter.objects.filter(user=user)

    filtered_requests, filter_form = handle_filters(request, initial_requests)

    context = {'requests': filtered_requests, 'filter_form': filter_form, 'saved_filters': saved_filters}
    return render(request, 'request/request_list.html', context)



# Функция для применения фильтров к QuerySet
def apply_filters(queryset, filters):
    for field, value in filters.items():
        if value:
            if isinstance(value, list) or isinstance(value, QuerySet):
                queryset = queryset.filter(**{f"{field}__in": value})
            elif isinstance(value, QuerySet) and value.count() == 1:
                queryset = queryset.filter(**{field: value.first()})
            else:
                queryset = queryset.filter(**{field: value})
    return queryset

@login_required
def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.requester = request.user
            priority = form.cleaned_data.get('priority')
            request_type = form.cleaned_data.get('request_type')

            duration_obj = PriorityDuration.objects.filter(priority=priority, request_type=request_type).first()
            if duration_obj:
                # Calculate the due date based on the duration_in_hours
                new_request.due_date = timezone.now() + timedelta(hours=duration_obj.duration_in_hours)

            new_request.save()
            return redirect('request_list')
    else:
        form = RequestForm()

    return render(request, 'request/request_create.html', {'form': form})


@login_required
def request_detail_update(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    user = request.user
    can_edit = user.has_perm('change_request') or user == request_instance.requester
    comments = Comment.objects.filter(request=request_instance)

    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.request = request_instance
                new_comment.author = user
                new_comment.save()
                return redirect('request_detail_update', pk=pk)
        elif 'submit_update' in request.POST:
            form = RequestForm(request.POST, instance=request_instance)
            if form.is_valid():
                form.save()
                # Call function to change request statuses
                update_request_status(request_instance)
                return redirect('request_detail_update', pk=pk)
        # Reinitialize the form for a GET request or if the form is not valid.
        form = RequestForm(instance=request_instance)
        comment_form = CommentForm()

    else:
        form = RequestForm(instance=request_instance)
        comment_form = CommentForm()

    context = {
        'request_instance': request_instance,
        'form': form,
        'can_edit': can_edit,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'request/request_detail_update.html', context)
