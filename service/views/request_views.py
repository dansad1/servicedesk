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


def request_list(request):
    user = request.user

    # Инициализация начального набора заявок
    if is_in_group(user, "Администратор"):
        initial_requests = Request.objects.all()
    else:
        initial_requests = Request.objects.filter(company=user.company)

    # Удаление фильтра, если указан
    delete_filter_id = request.GET.get('delete_filter')
    if delete_filter_id:
        SavedFilter.objects.filter(id=delete_filter_id, user=user).delete()

    # Загрузка и применение сохраненного фильтра, если указан
    load_filter_id = request.GET.get('load_filter')
    if load_filter_id:
        try:
            saved_filter = SavedFilter.objects.get(id=load_filter_id, user=user)
            loaded_filters = saved_filter.filter_data

            # Удаление ключа 'unknown', если он присутствует
            loaded_filters.pop('unknown', None)

            # Применение фильтров
            initial_requests = apply_filters(initial_requests, loaded_filters)
        except SavedFilter.DoesNotExist:
            pass

    # Получение всех сохраненных фильтров для текущего пользователя
    saved_filters = SavedFilter.objects.filter(user=user)

    # Инициализация формы фильтрации
    filter_form = RequestFilterForm(request.GET or None, initial=request.session.get('saved_filters', {}))

    # Логика для сохранения фильтров
    if 'saveFilter' in request.GET:
        filter_name = request.GET.get('filter_name')
        if filter_name:
            new_filter = SavedFilter(user=user, filter_name=filter_name, filter_data=request.GET.dict())
            new_filter.save()

    # Логика применения фильтров
    if request.method == "GET" and filter_form.is_valid():
        filters = filter_form.cleaned_data

        # Преобразование QuerySet в список
        serializable_filters = {}
        for key, value in filters.items():
            if isinstance(value, QuerySet) or isinstance(value, list):
                serializable_filters[key] = [str(v.id) for v in value]
            elif hasattr(value, 'id'):
                serializable_filters[key] = str(value.id)
            else:
                serializable_filters[key] = value

        request.session['saved_filters'] = serializable_filters  # Сохраняем фильтры в сессии

        if 'filter_name' in filters:
            del filters['filter_name']  # Удаляем ключ 'filter_name'

        filtered_requests = apply_filters(initial_requests, filters)  # Применяем фильтры
    else:
        filtered_requests = initial_requests

    context = {'requests': filtered_requests, 'filter_form': filter_form, 'saved_filters': saved_filters}
    return render(request, 'request/request_list.html', context)

def apply_filters(queryset, filters):
    for field, value in filters.items():
        if value:
            if isinstance(value, list) or isinstance(value, QuerySet):  # Для полей, которые принимают несколько значений
                queryset = queryset.filter(**{f"{field}__in": value})
            elif isinstance(value, QuerySet) and value.count() == 1:  # Для QuerySet с одним значением
                queryset = queryset.filter(**{field: value.first()})
            else:  # Для всех остальных случаев
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
    can_mark_completed = can_edit or user.has_perm('change_request') or user == request_instance.assignee

    comment_form = CommentForm()
    comments = Comment.objects.filter(request=request_instance)

    if request.method == 'POST':
        mark_completed = request.POST.get('mark_completed', False)
        if mark_completed:
            status_completed, created = Status.objects.get_or_create(name="Выполнена")
            request_instance.status = status_completed
            request_instance.save()
            return redirect('request_detail_update', pk=pk)

        form = RequestForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()

            # Вызов функции для смены статусов
            update_request_status(request_instance)

            return redirect('request_detail_update', pk=pk)
    else:
        form = RequestForm(instance=request_instance)

    context = {
        'request_instance': request_instance,
        'form': form,
        'can_edit': can_edit,
        'can_mark_completed': can_mark_completed,
        'comment_form': comment_form,
        'comments': comments,
    }

    return render(request, 'request/request_detail_update.html', context)