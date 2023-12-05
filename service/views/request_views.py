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
from ..permissions import can_view_request,can_edit_request


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
def add_comment(request, request_instance, comment_form):
    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.request = request_instance
        new_comment.author = request.user
        if 'attachment' in request.FILES:
            new_comment.attachment = request.FILES['attachment']
        new_comment.save()
        messages.success(request, "Your comment has been added.")
    else:
        messages.error(request, "Error in comment form.")
@login_required
def update_request(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    is_editable = request.user.has_perm('service.action_edit_request', request_instance)

    if request.method == 'POST' and 'submit_update' in request.POST and is_editable:
        form = RequestForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()
            return redirect('request_list')  # или другой URL, куда вы хотите перенаправить пользователя
    else:
        form = RequestForm(instance=request_instance)

    return render(request, 'request/request_update.html', {
        'form': form,
        'is_editable': is_editable,
        'request_instance': request_instance
    })
@login_required
def request_list(request):
    filter_form = RequestFilterForm(request.GET)
    initial_requests = Request.objects.all()

    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        filtered_requests = apply_filters(initial_requests, filters)
    else:
        filtered_requests = initial_requests

    requests_with_action = []

    for req in filtered_requests:
        # Определение действия на основе прав доступа
        action_url = 'view_request'  # URL страницы просмотра по умолчанию
        if can_edit_request(request.user, req):
            action_url = 'edit_request'  # URL страницы редактирования, если есть право на редактирование

        requests_with_action.append({'request': req, 'action_url': action_url})

    return render(request, 'request/request_list.html', {
        'requests_with_action': requests_with_action,
        'filter_form': filter_form
    })