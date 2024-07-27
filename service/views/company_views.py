from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from service.forms.Company_forms import CompanyForm,DepartmentForm
from django.urls import reverse_lazy
from service.models import CustomUser, Company, Request, Status,Department
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from ..permissions import *
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib import messages


@login_required
def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            new_company = form.save()
            return redirect('company_edit', pk=new_company.pk)
    else:
        form = CompanyForm()

    return render(request, 'company/company_create.html', {'form': form})


@login_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(instance=company)
    employees = company.customuser_set.all()

    # Получение всех заявок, связанных с компанией через динамические поля
    employee_ids = employees.values_list('id', flat=True)
    company_requests = Request.objects.filter(
        field_values__field_meta__name='Requester',
        field_values__value_requester__in=employee_ids
    ).select_related('request_type', 'request_type__field_set')

    departments = company.departments.all()
    subdepartments = Department.objects.filter(parent__company=company).select_related('parent')

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Информация о компании обновлена.")
            return redirect('company_edit', pk=company.pk)

    context = {
        'form': form,
        'company': company,
        'employees': employees,
        'requests': company_requests,
        'departments': departments,
        'subdepartments': subdepartments,
    }
    return render(request, 'company/company_edit.html', context)
@login_required
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'company/company_list.html', {'companies': companies})
@require_http_methods(["POST"])
@login_required
def company_delete(request, pk):
    if request.method == 'POST':
        company_ids = request.POST.getlist('selected_companies')
        if company_ids:
            Company.objects.filter(id__in=company_ids).delete()
            messages.success(request, 'Выбранные компании были удалены.')
        else:
            messages.warning(request, 'Пожалуйста, выберите хотя бы одну компанию для удаления.')
    return redirect('company_list')
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
