from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from service.forms.Company_forms import CompanyForm,DepartmentForm
from django.urls import reverse_lazy
from service.models import CustomUser, Company, Request, Status, Department, CompanyFieldSet, CompanyFieldValue
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from service.models import CompanyFieldMeta
from service.forms.Company_forms import CompanyFieldMetaForm


# Представление для создания нового поля компании
# Представление для создания нового поля CompanyFieldMeta
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
            return redirect('company_field_meta_list')  # Перенаправление на список полей после сохранения
    else:
        form = CompanyFieldMetaForm(instance=field_meta)

    return render(request, 'company/company_field_meta_edit.html', {
        'form': form,
        'title': 'Редактировать поле компании',
    })


# Представление для отображения списка полей CompanyFieldMeta
def company_field_meta_list(request):
    field_metas = CompanyFieldMeta.objects.all()
    return render(request, 'company/company_field_meta_list.html', {
        'field_metas': field_metas,
        'title': 'Список полей компании',
    })
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

def company_edit(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_list')  # Перенаправление на список компаний после сохранения
    else:
        form = CompanyForm(instance=company)

    return render(request, 'company/company_edit.html', {
        'form': form,
        'title': 'Редактировать компанию',
    })

def company_list(request):
    """Отображает список всех компаний"""
    companies = Company.objects.all()
    return render(request, 'company/company_list.html', {
        'companies': companies,
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
