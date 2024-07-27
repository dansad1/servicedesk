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
import json
from django.views.decorators.csrf import csrf_exempt


def handle_filters(request, initial_requests, form):
    load_filter_id = request.GET.get('load_filter')
    loaded_filters = {}

    if load_filter_id:
        try:
            saved_filter = SavedFilter.objects.get(id=load_filter_id, user=request.user)
            loaded_filters = json.loads(saved_filter.filter_data)
            loaded_filters.pop('filter_name', None)
            initial_requests = apply_optional_filters(initial_requests, loaded_filters)
        except (SavedFilter.DoesNotExist, json.JSONDecodeError):
            pass

    if request.method == "GET" and form.is_valid():
        filters = form.cleaned_data
        filters.pop('filter_name', None)
        filtered_requests = apply_optional_filters(initial_requests, filters)
    else:
        filtered_requests = initial_requests

    return filtered_requests, form
def apply_optional_filters(queryset, filters):
    for field, value in filters.items():
        if value:
            if isinstance(value, list) or isinstance(value, QuerySet):
                queryset = queryset.filter(**{f"field_values__field_meta__name": field, f"field_values__value_text__in": value})
            else:
                queryset = queryset.filter(**{f"field_values__field_meta__name": field, f"field_values__value_text": value})
    return queryset

def select_request_type(request):
    types = RequestType.objects.all()
    return render(request, 'request/select_request_type.html', {'types': types})

@login_required
def request_create(request, request_type_id):
    request_type = get_object_or_404(RequestType, id=request_type_id)
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES, user=request.user, request_type=request_type)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.request_type = request_type
            new_request.save()
            for field_name, field_value in form.cleaned_data.items():
                if field_name.startswith('custom_field_'):
                    field_id = int(field_name.split('_')[-1])
                    field_meta = get_object_or_404(FieldMeta, id=field_id)
                    if field_meta.field_type == 'comment':
                        if field_value[0].strip() or field_value[1]:
                            comment = Comment(
                                request=new_request,
                                author=request.user,
                                text=field_value[0],
                                attachment=field_value[1]
                            )
                            comment.save()
                    elif field_meta.field_type == 'description':
                        if field_value[0].strip() or field_value[1]:
                            description = FieldValue(
                                request=new_request,
                                field_meta=field_meta
                            )
                            description.set_value(f"{field_value[0]},{field_value[1]}")
                            description.save()
                    else:
                        field_value_obj, created = FieldValue.objects.get_or_create(
                            request=new_request,
                            field_meta=field_meta
                        )
                        field_value_obj.set_value(field_value)
                        field_value_obj.save()

            return redirect('request_list')
    else:
        form = RequestForm(user=request.user, request_type=request_type)

    excluded_fields = ['title', 'description', 'attachment', 'request_type']
    return render(request, 'request/request_create.html', {
        'form': form,
        'request_type': request_type,
        'excluded_fields': excluded_fields,
    })
@login_required
def request_edit(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    request_type = req.request_type
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES, instance=req, user=request.user, request_type=request_type)
        if form.is_valid():
            req = form.save()
            for field_name, field_value in form.cleaned_data.items():
                if field_name.startswith('custom_field_'):
                    field_id = int(field_name.split('_')[-1])
                    field_meta = get_object_or_404(FieldMeta, id=field_id)
                    if field_meta.field_type == 'comment':
                        if field_value[0].strip() or field_value[1]:
                            comment = Comment(
                                request=req,
                                author=request.user,
                                text=field_value[0],
                                attachment=field_value[1]
                            )
                            comment.save()
                    elif field_meta.field_type == 'description':
                        if field_value[0].strip() or field_value[1]:
                            description = FieldValue(
                                request=req,
                                field_meta=field_meta
                            )
                            description.set_value(f"{field_value[0]},{field_value[1]}")
                            description.save()
                    else:
                        field_value_obj, created = FieldValue.objects.get_or_create(
                            request=req,
                            field_meta=field_meta
                        )
                        field_value_obj.set_value(field_value)
                        field_value_obj.save()

            return redirect('request_list')
    else:
        form = RequestForm(instance=req, user=request.user, request_type=request_type)

    return render(request, 'request/request_edit.html', {
        'form': form,
        'request': req,
        'excluded_fields': ['title', 'description', 'attachment', 'request_type']
    })


@login_required
def request_list(request):
    fieldset, created = FieldSet.objects.get_or_create(name="Request Filters")
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
            'field_values': {field.name: req.get_field_values().get(field.name) for field in fieldset.fields.all()}
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