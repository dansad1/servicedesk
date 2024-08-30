from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from service.forms.Company_forms import CompanyForm, DepartmentForm, FieldVisibilityForm, CompanyCustomFieldMetaForm, \
    StandardFieldsFilterForm
from django.urls import reverse_lazy
from service.models import CustomUser, Company, Request, Status, Department, CompanyFieldSet, CompanyFieldValue, CompanyCustomFieldMeta
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from service.models import CompanyFieldMeta
from service.forms.Company_forms import CompanyFieldMetaForm
from django.http import JsonResponse


# Представление для создания нового поля компании
def company_field_meta_create(request):
    if request.method == 'POST':
        form = CompanyFieldMetaForm(request.POST)
        if form.is_valid():
            field_meta = form.save()

            return redirect('company_field_meta_list')  # Перенаправление на список полей после сохранения
    else:
        form = CompanyFieldMetaForm()

    return render(request, 'company/company_field_meta_create.html', {
        'form': form,
        'title': 'Создать поле компании',
    })


# Представление для редактирования существующего поля CompanyFieldMeta
def company_field_meta_edit(request, field_meta_id):
    field_meta = get_object_or_404(CompanyFieldMeta, id=field_meta_id)
    if request.method == 'POST':
        form = CompanyFieldMetaForm(request.POST, instance=field_meta)
        if form.is_valid():
            form.save()
            return redirect('standard_fields_list')  # Перенаправление на правильный список полей
    else:
        form = CompanyFieldMetaForm(instance=field_meta)

    return render(request, 'company/company_field_meta_edit.html', {
        'form': form,
        'title': 'Редактировать поле компании',
    })



# Представление для отображения списка полей CompanyFieldMeta


@login_required
def standard_fields_list(request):
    # Получаем все стандартные поля
    standard_fields = CompanyFieldMeta.objects.all()

    context = {
        'standard_fields': standard_fields,
        'title': 'Список стандартных полей компании',
    }

    return render(request, 'company/standard_fields_list.html', context)

def company_field_meta_delete(request, field_meta_id):
    """Удаление существующего поля компании"""
    field_meta = get_object_or_404(CompanyFieldMeta, id=field_meta_id)
    if request.method == 'POST':
        field_meta.delete()
        return redirect('company_field_meta_list')

    return render(request, 'company/company_field_meta_confirm_delete.html', {
        'field_meta': field_meta,
        'title': 'Удалить поле компании',
    })

def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            return redirect('company_list')  # Перенаправление на список компаний после сохранения
    else:
        form = CompanyForm()

    return render(request, 'company/company_create.html', {
        'form': form,
        'title': 'Создать компанию',
    })


@login_required
def company_edit(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    employees = CustomUser.objects.filter(company=company)

    company_requests = Request.objects.filter(
        field_values__field_meta__name='Requester',
        field_values__value_requester__in=employees.values_list('id', flat=True)
    ).select_related('request_type', 'request_type__field_set')

    hidden_fields = company.hidden_fields.all()
    visible_field_names = [f'field_{field_meta.id}' for field_meta in CompanyFieldMeta.objects.exclude(id__in=hidden_fields.values_list('id', flat=True))]

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Информация о компании обновлена.")
            return redirect('company_edit', company_id=company.id)
    else:
        form = CompanyForm(instance=company)

    # Словарь для отображения кастомных полей
    custom_fields_form_data = {
        f'custom_field_{custom_field.id}': form[f'custom_field_{custom_field.id}']
        for custom_field in company.custom_field_meta.all()
        if custom_field not in company.hidden_custom_fields.all()
    }

    context = {
        'form': form,
        'custom_fields_form_data': custom_fields_form_data,  # Добавлено
        'title': 'Редактировать компанию',
        'company': company,
        'employees': employees,
        'requests': company_requests,
        'visible_field_names': visible_field_names,
    }

    return render(request, 'company/company_edit.html', context)



@login_required
def manage_fields_visibility(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        if 'delete_custom_field' in request.POST:
            # Получаем ID кастомного поля из POST запроса
            custom_field_id = request.POST.get('delete_custom_field')
            try:
                custom_field = CompanyCustomFieldMeta.objects.get(id=custom_field_id, company=company)
                custom_field.delete()
                messages.success(request, f"Кастомное поле '{custom_field.name}' было удалено.")
            except CompanyCustomFieldMeta.DoesNotExist:
                messages.error(request, "Кастомное поле не найдено или уже было удалено.")
        else:
            form = FieldVisibilityForm(request.POST, company=company)
            if form.is_valid():
                hidden_standard_fields = []
                hidden_custom_fields = []

                # Обработка видимости стандартных полей
                for field_meta in CompanyFieldMeta.objects.all():
                    field_visibility_key = f"visible_{field_meta.id}"
                    if not form.cleaned_data.get(field_visibility_key):
                        hidden_standard_fields.append(field_meta)

                # Обработка видимости кастомных полей
                for custom_field_meta in company.custom_field_meta.all():
                    custom_field_visibility_key = f"visible_custom_{custom_field_meta.id}"
                    if not form.cleaned_data.get(custom_field_visibility_key):
                        hidden_custom_fields.append(custom_field_meta)

                # Установка скрытых полей
                company.hidden_fields.set(hidden_standard_fields)
                company.hidden_custom_fields.set(hidden_custom_fields)
                messages.success(request, "Видимость полей обновлена.")

                # Редирект на страницу редактирования компании
                return redirect(reverse('company_edit', args=[company_id]))
    else:
        form = FieldVisibilityForm(company=company)

    # Разделяем поля формы на стандартные и кастомные
    standard_field_form_fields = [
        field for field in form if field.name.startswith('visible_') and not field.name.startswith('visible_custom_')
    ]
    custom_field_form_fields = [
        {'field': field, 'id': field.name.split('_')[2]}  # Сохраняем id поля в словаре
        for field in form if field.name.startswith('visible_custom_')
    ]

    context = {
        'form': form,
        'standard_field_form_fields': standard_field_form_fields,
        'custom_field_form_fields': custom_field_form_fields,
        'company': company,
        'standard_fields': CompanyFieldMeta.objects.all(),
        'hidden_fields': company.hidden_fields.all(),
        'custom_fields': company.custom_field_meta.all(),
        'hidden_custom_fields': company.hidden_custom_fields.all(),
    }

    return render(request, 'company/manage_fields_visibility.html', context)





def company_list(request):
    """Отображает список всех компаний с фильтрацией по стандартным полям"""

    # Инициализация формы фильтрации
    form = StandardFieldsFilterForm(request.GET or None)

    # Получаем все компании
    companies = Company.objects.all()

    # Применяем фильтры, если они есть
    if form.is_valid():
        for field_name, value in form.cleaned_data.items():
            if value:
                # Получаем метаданные поля по имени
                field_meta_name = field_name.replace('_', ' ')
                try:
                    field_meta = CompanyFieldMeta.objects.get(name__iexact=field_meta_name)
                    field_values = CompanyFieldValue.objects.filter(
                        company_field_meta=field_meta,
                        **{f'value_{field_meta.field_type}__icontains': value}
                    )
                    company_ids = field_values.values_list('company_id', flat=True)
                    companies = companies.filter(id__in=company_ids)
                except CompanyFieldMeta.DoesNotExist:
                    pass

    # Подготовка данных для отображения
    companies_with_field_values = [
        {
            'company': company,
            'field_values': company.get_field_values()
        }
        for company in companies
    ]

    return render(request, 'company/company_list.html', {
        'companies_with_field_values': companies_with_field_values,
        'filter_form': form,
        'title': 'Список компаний',
    })
def company_delete(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        company.delete()
        return redirect('company_list')  # Перенаправление на список компаний после удаления

    return render(request, 'company/company_confirm_delete.html', {
        'company': company,
        'title': 'Удалить компанию',
    })

def company_custom_field_meta_create(request, company_id):
    """Создание нового кастомного поля для компании"""
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        form = CompanyCustomFieldMetaForm(request.POST)
        if form.is_valid():
            custom_field_meta = form.save(commit=False)
            custom_field_meta.company = company
            custom_field_meta.save()
            return redirect('company_edit', company_id=company.id)  # Перенаправление на страницу редактирования компании
    else:
        form = CompanyCustomFieldMetaForm()

    return render(request, 'company/company_custom_field_meta_create.html', {
        'form': form,
        'title': 'Создать кастомное поле для компании',
        'company': company,
    })


def company_custom_field_meta_edit(request, custom_field_meta_id):
    """Редактирование существующего кастомного поля компании"""
    custom_field_meta = get_object_or_404(CompanyCustomFieldMeta, id=custom_field_meta_id)
    company = custom_field_meta.company

    if request.method == 'POST':
        form = CompanyCustomFieldMetaForm(request.POST, instance=custom_field_meta)
        if form.is_valid():
            form.save()
            return redirect('company_edit', company_id=company.id)  # Перенаправление на страницу редактирования компании
    else:
        form = CompanyCustomFieldMetaForm(instance=custom_field_meta)

    return render(request, 'company/company_custom_field_meta_edit.html', {
        'form': form,
        'title': 'Редактировать кастомное поле компании',
        'company': company,
    })

@login_required
def company_custom_field_meta_delete(request, custom_field_meta_id):
    """Удаление кастомного поля компании"""
    custom_field_meta = get_object_or_404(CompanyCustomFieldMeta, id=custom_field_meta_id)
    company = custom_field_meta.company

    if request.method == 'POST':
        custom_field_meta.delete()
        messages.success(request, f"Кастомное поле '{custom_field_meta.name}' было успешно удалено.")
        return redirect('manage_fields_visibility', company_id=company.id)  # Перенаправление на управление видимостью полей компании

    return redirect('manage_fields_visibility', company_id=company.id)



@login_required
def department_create(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, company_id=company.id)
        if form.is_valid():
            department = form.save(commit=False)
            department.company = company
            department.save()
            form.save_m2m()
            messages.success(request, 'Отдел успешно создан.')
            return redirect('company_edit', pk=company.pk)
    else:
        form = DepartmentForm(initial={'company': company.id}, company_id=company.id)
        form.fields['users'].queryset = CustomUser.objects.filter(company=company)

    context = {'form': form, 'company': company}
    return render(request, 'company/department_create.html', context)

@login_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    # Исправление фильтрации по правильным полям
    department_requests = Request.objects.filter(
        field_values__field_meta__name='Requester',
        field_values__value_requester__department=department
    ).distinct()

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department, company_id=department.company_id)
        if form.is_valid():
            department = form.save()
            messages.success(request, "Отдел обновлён.")
            return redirect('company_edit', pk=department.company.pk)
    else:
        form = DepartmentForm(instance=department, company_id=department.company_id)

    context = {
        'form': form,
        'department': department,
        'company': department.company,
        'department_requests': department_requests,
    }
    return render(request, 'company/department_edit.html', context)

@login_required
@require_http_methods(["POST"])
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    company_pk = department.company.pk
    department.delete()
    messages.success(request, "Отдел удалён.")
    return redirect('company_edit', pk=company_pk)

@login_required
def subdepartment_create(request, department_id):
    parent_department = get_object_or_404(Department, pk=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            subdepartment = form.save(commit=False)
            subdepartment.parent_department = parent_department
            subdepartment.company = parent_department.company
            subdepartment.save()
            messages.success(request, 'Подотдел успешно создан.')
            return redirect('department_edit', pk=parent_department.pk)
    else:
        form = DepartmentForm()

    return render(request, 'company/subdepartment_create.html', {'form': form, 'parent_department': parent_department})
def ajax_filter_companies(request):
    """Асинхронная фильтрация компаний по стандартным полям"""
    form = StandardFieldsFilterForm(request.GET or None)
    companies = Company.objects.all()

    if form.is_valid():
        for field_name, value in form.cleaned_data.items():
            if value:
                field_meta_name = field_name.replace('_', ' ')
                try:
                    field_meta = CompanyFieldMeta.objects.get(name__iexact=field_meta_name)
                    field_values = CompanyFieldValue.objects.filter(
                        company_field_meta=field_meta,
                        **{f'value_{field_meta.field_type}__icontains': value}
                    )
                    company_ids = field_values.values_list('company_id', flat=True)
                    companies = companies.filter(id__in=company_ids)
                except CompanyFieldMeta.DoesNotExist:
                    pass

    # Преобразование результатов в JSON
    data = [
        {
            'id': company.id,
            'name': company.name,
            'fields': company.get_field_values(),
        }
        for company in companies
    ]

    return JsonResponse(data, safe=False)