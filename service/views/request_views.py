import json
import logging
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils.formats import date_format
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, TableStyle, Table
from django.contrib import messages

from service.models import *
from ..forms.Request_forms import *
from ..models import SavedFilter

logger = logging.getLogger(__name__)

def handle_filters(request, initial_requests, form):
    """
    Обрабатывает фильтры и возвращает отфильтрованные заявки.
    """
    load_filter_id = request.GET.get('load_filter')
    loaded_filters = {}

    # Загрузка сохраненного фильтра
    if load_filter_id:
        try:
            saved_filter = SavedFilter.objects.get(id=load_filter_id, user=request.user)
            loaded_filters = json.loads(saved_filter.filter_data)
            loaded_filters.pop('filter_name', None)
            initial_requests = apply_optional_filters(initial_requests, loaded_filters)
        except SavedFilter.DoesNotExist:
            logger.warning(f"Сохраненный фильтр с ID {load_filter_id} не найден для пользователя {request.user}.")
        except json.JSONDecodeError:
            logger.error(f"Ошибка декодирования JSON для фильтра ID {load_filter_id}.")

    # Обработка данных формы
    if request.method == "GET" and form.is_valid():
        filters = form.cleaned_data
        filters.pop('filter_name', None)
        filtered_requests = apply_optional_filters(initial_requests, filters)
    else:
        filtered_requests = initial_requests

    return filtered_requests, form


def apply_optional_filters(queryset, filters):
    """
    Применяет фильтры к QuerySet на основе переданных данных.
    """
    for field, value in filters.items():
        if value:
            try:
                if isinstance(value, (list, QuerySet)):
                    # Фильтрация по списку значений
                    queryset = queryset.filter(
                        Q(field_values__field_meta__name=field) &
                        Q(field_values__value_text__in=value)
                    )
                else:
                    # Фильтрация по одному значению
                    queryset = queryset.filter(
                        Q(field_values__field_meta__name=field) &
                        Q(field_values__value_text=value)
                    )
            except Exception as e:
                logger.error(f"Ошибка применения фильтра {field}={value}: {e}")
    return queryset
def select_request_type(request):
    types = RequestType.objects.all()
    return render(request, 'request/select_request_type.html', {'types': types})

@login_required
def request_create(request, request_type_id):
    # Получаем объект RequestType по ID
    request_type = get_object_or_404(RequestType, id=request_type_id)

    if request.method == 'POST':
        # Передаем request_type в initial и user
        form = RequestForm(request.POST, request.FILES, user=request.user, initial={'request_type': request_type})
        if form.is_valid():
            form.save()
            return redirect('request_list')
    else:
        # Передаем request_type в initial для GET-запроса
        form = RequestForm(user=request.user, initial={'request_type': request_type})

    return render(request, 'request/request_create.html', {
        'form': form,
        'request_type': request_type
    })
def request_edit(request, request_id):
    # Получаем существующую заявку
    existing_request = get_object_or_404(Request, id=request_id)

    if request.method == "POST":
        # Создаем форму с переданными данными и существующей заявкой
        form = RequestForm(request.POST, instance=existing_request, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('request_list')  # Перенаправляем пользователя на список заявок
    else:
        # Создаем форму с данными существующей заявки
        form = RequestForm(instance=existing_request, user=request.user)

    return render(request, 'request/request_edit.html', {'form': form})
def calculate_due_date(request_instance):
    """Рассчитывает и возвращает значение due_date для кастомного поля на основе приоритета."""
    priority_value = request_instance.field_values.filter(field_meta__field_type='priority').first()
    if priority_value:
        priority_duration = PriorityDuration.objects.filter(
            request_type=request_instance.request_type,
            priority=priority_value.value_priority
        ).first()
        if priority_duration:
            return request_instance.created_at + timedelta(hours=priority_duration.duration_in_hours)
    return None

@login_required
def request_list(request):
    fieldset, created = RequestFieldSet.objects.get_or_create(name="Request Filters")
    if created:
        fieldset.add_default_fields()

    RequestFilterForm = generate_dynamic_form(fieldset)
    form = RequestFilterForm(request.GET or None)

    initial_requests = Request.objects.all()
    filtered_requests, filter_form = handle_filters(request, initial_requests, form)

    if request.method == "POST" and 'save_filter' in request.POST:
        save_filter_form = SavedFilterForm(request.POST)
        if save_filter_form.is_valid():
            saved_filter = save_filter_form.save(commit=False)
            saved_filter.user = request.user
            saved_filter.filter_data = json.dumps(request.GET)
            saved_filter.save()
            return redirect('request_list')
    else:
        save_filter_form = SavedFilterForm()

    requests_with_field_values = [
        {
            'request': req,
            'field_values': req.get_field_values()
        }
        for req in filtered_requests
    ]

    saved_filters = SavedFilter.objects.filter(user=request.user)

    return render(request, 'request/request_list.html', {
        'requests_with_field_values': requests_with_field_values,
        'filter_form': filter_form,
        'save_filter_form': save_filter_form,
        'saved_filters': saved_filters,
        'fieldset': fieldset,
    })




@login_required
def request_delete(request):
    if request.method == 'POST':
        request_ids = request.POST.getlist('selected_requests')
        if request_ids:
            Request.objects.filter(id__in=request_ids).delete()
            messages.success(request, 'Выбранные заявки были удалены.')
        else:
            messages.warning(request, 'Пожалуйста, выберите хотя бы одну заявку для удаления.')
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