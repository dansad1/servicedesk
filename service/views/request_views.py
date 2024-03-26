from django.core.checks import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, TableStyle,Table

from service.models import CustomUser, Company,Request,Status,RequestType
from service.forms.Company_forms import  CompanyForm
from django.contrib.auth import login
from service.forms.User_forms import CustomUserCreationForm
from django.urls import reverse_lazy
from  service.forms import *
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required,user_passes_test
from django.contrib.auth.models import Group
from django.utils import timezone
from service.models import *
from datetime import timedelta

from ..forms.Request_forms import *
from ..status_logic import *
from ..models import SavedFilter
from django.db.models import QuerySet
import json
from django.core.exceptions import ValidationError
import json
from django.contrib import messages
from ..permissions import can_view_request,can_edit_request
from django.http import HttpResponse, HttpResponseRedirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from django.utils.formats import date_format

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
def select_request_type(request):
    types = RequestType.objects.all()
    return render(request, 'request/select_request_type.html', {'types': types})

@login_required
def request_create(request, type_id):
    request_type = get_object_or_404(RequestType, pk=type_id)
    form = RequestForm(request.POST or None, request.FILES or None)
    comment_form = CommentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.requester = request.user
            new_request.request_type = request_type

            priority = form.cleaned_data.get('priority')
            duration_obj = PriorityDuration.objects.filter(priority=priority, request_type=request_type).first()
            if duration_obj:
                new_request.due_date = timezone.now() + timedelta(hours=duration_obj.duration_in_hours)

            new_request.save()
            form.save_m2m()

            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.request = new_request
                new_comment.author = request.user
                new_comment.save()

            # Определяем, какая кнопка была нажата
            if 'save_and_close' in request.POST:
                messages.success(request, "Заявка успешно создана.")
                return redirect('request_list')
            else:
                messages.success(request, "Заявка создана. Вы можете продолжить редактирование.")
                return redirect('request_edit', pk=new_request.pk)

    context = {
        'form': form,
        'comment_form': comment_form,
        'request_type': request_type
    }
    return render(request, 'request/request_create.html', context)
@login_required
def add_comment(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.request = request_instance
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, "Комментарий успешно добавлен.")
            return HttpResponseRedirect(request.path_info)  # Остаться на текущей странице
    else:
        comment_form = CommentForm()

    # Возвращаем форму создания заявки для отображения вместе с формой комментариев
    form = RequestForm()
    context = {
        'form': form,
        'comment_form': comment_form,
        'request_instance': request_instance,
        'request_type': request_instance.request_type  # Или другой контекст, необходимый для шаблона
    }
    return render(request, 'request/request_create.html', context)
@login_required
def request_edit(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    is_editable = request.user.has_perm('service.action_edit_request', request_instance)

    if request.method == 'POST' and 'submit_update' in request.POST and is_editable:
        form = RequestForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()
            return redirect('request_list')  # или другой URL, куда вы хотите перенаправить пользователя
    else:
        form = RequestForm(instance=request_instance)

    return render(request, 'request/request_edit.html', {
        'form': form,
        'is_editable': is_editable,
        'request_instance': request_instance,
        'due_date': request_instance.due_date
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
def request_delete(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        request_instance.delete()
        messages.success(request, "Заявка успешно удалена.")
        return redirect('request_list')

    # Нет необходимости в отдельном шаблоне для подтверждения удаления
    return redirect('request_list')


pdfmetrics.registerFont(
    TTFont('Arial', 'staticfiles/fonts/ArialRegular.ttf'))  # Убедитесь, что файл шрифта находится в указанной директории


def export_requests_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="requests.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    data = [
        ["Название заявки", "Статус", "Приоритет", "Исполнитель", "Заявитель", "Срок выполнения", "Время обновления"]]

    # Добавление данных из объектов Request
    for req in Request.objects.all():
        row = [
            req.title,
            req.status,
            req.priority,
            req.assignee.username if req.assignee else 'Не назначен',
            req.requester.username if req.requester else 'Не указано',
            date_format(req.due_date, "d.m.Y") if req.due_date else 'Не указано',
            date_format(req.updated_at, "d.m.Y H:i") if req.updated_at else 'Не указано',
        ]
        data.append(row)

    # Создание таблицы ReportLab
    table = Table(data)

    # Стиль таблицы
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),  # Заголовок
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#333333")),  # Цвет текста заголовка
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Выравнивание текста
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),  # Шрифт для всей таблицы
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Размер шрифта для всей таблицы
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),  # Отступ снизу
        ('TOPPADDING', (0, 0), (-1, -1), 8),  # Отступ сверху
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#dddddd")),  # Границы
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),  # Цвет фона строк
    ])

    table.setStyle(style)

    elements.append(table)
    doc.build(elements)

    return response