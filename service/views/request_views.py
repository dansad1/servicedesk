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
from django.contrib.auth.models import Group
from django.utils import timezone
from service.models import *
from datetime import timedelta
from ..status_logic import *
from ..models import SavedFilter
from django.db.models import QuerySet
import json
from django.core.exceptions import ValidationError
import json
from django.contrib import messages
from ..permissions import  can_view_request


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

    filter_form = RequestFilterForm(request.GET)
    initial_requests = Request.objects.all()  # Замените на вашу модель запросов

    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        filtered_requests = apply_filters(initial_requests, filters)
    else:
        filtered_requests = initial_requests
    return render(request, 'request/request_list.html', {'requests': filtered_requests, 'filter_form': filter_form})


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
    original_status = request_instance.status  # Сохраняем первоначальный статус

    if not request.user.has_perm('change_request') and request.user != request_instance.requester:
        messages.error(request, "You do not have the permission to edit this request.")
        return redirect('request_detail', pk=pk)  # Предполагается, что у вас есть такой URL

    comment_form = CommentForm()
    form = RequestForm(instance=request_instance, current_status=request_instance.status)

    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            comment_form = CommentForm(request.POST, request.FILES)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.request = request_instance
                new_comment.author = request.user
                if 'attachment' in request.FILES:
                    new_comment.attachment = request.FILES['attachment']
                new_comment.save()
                messages.success(request, "Your comment has been added.")
                return redirect('request_detail_update', pk=pk)
            elif 'submit_update' in request.POST:
                form = RequestForm(request.POST, request.FILES, instance=request_instance,
                                   current_status=original_status)
                if form.is_valid():
                    # Сохраняем форму без коммита для дальнейшей обработки
                    request_instance = form.save(commit=False)

                    # Check if there is an attachment in the POST request and handle it
                    if 'attachment' in request.FILES:
                        request_instance.attachment = request.FILES['attachment']

                    # Обновляем статус заявки, если это необходимо
                    check_and_update_request_status(request_instance, original_status)

                    # Сохраняем заявку
                    request_instance.save()
                    form.save_m2m()  # Необходимо для сохранения данных many-to-many полей

                    messages.success(request, "The request has been updated.")
                    return redirect('request_detail_update', pk=pk)
                else:
                    messages.error(request, "There was an error with the form.")
    comments = Comment.objects.filter(request=request_instance)
    context = {
        'request_instance': request_instance,
        'form': form,
        'can_edit': True,  # Вы уже проверили права доступа в начале
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'request/request_detail_update.html', context)