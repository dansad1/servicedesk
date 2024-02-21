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

# Создание компании
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

# Редактирование компании
@login_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(instance=company, company_id=company.pk)  # Добавлено company_id
    employees = company.customuser_set.all()
    company_requests = Request.objects.filter(requester__in=employees).select_related('requester', 'assignee', 'status', 'priority', 'request_type')

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company, company_id=company.pk)
        if form.is_valid():
            form.save()
            messages.success(request, "Информация о компании обновлена.")
            return redirect('company_edit', pk=company.pk)

    context = {
        'form': form,
        'company': company,
        'employees': employees,
        'requests': company_requests,
    }
    return render(request, 'company/company_edit.html', context)


# Вывод списка компаний
@login_required
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'company/company_list.html', {'companies': companies})


# Создание департамента
@login_required
def create_department(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk)
    if request.method == 'POST':
        department_form = DepartmentForm(request.POST)
        if department_form.is_valid():
            new_department = department_form.save(commit=False)
            new_department.company = company
            new_department.save()
            messages.success(request, 'Отдел успешно создан.')
            return redirect('company_detail', pk=company.pk)
        else:
            # Если форма не валидна, добавляем сообщение об ошибке
            messages.error(request, 'Ошибка при создании отдела. Пожалуйста, проверьте введенные данные.')
    return redirect('company_detail', pk=company.pk)


# создание подепартамента
@login_required
def create_subdepartment(request, department_id):
    parent_department = get_object_or_404(Department, pk=department_id)
    if request.method == 'POST':
        subdepartment_form = DepartmentForm(request.POST)
        if subdepartment_form.is_valid():
            new_subdepartment = subdepartment_form.save(commit=False)
            new_subdepartment.parent_department = parent_department
            new_subdepartment.company = parent_department.company
            new_subdepartment.save()
            return redirect('company_detail', pk=parent_department.company.pk)
    return redirect('company_detail', pk=parent_department.company.pk)



@require_http_methods(["POST"])
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company.delete()
    messages.success(request, "Компания успешно удалена.")
    return redirect('company_list')