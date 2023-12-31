from django.shortcuts import render, redirect
from service.forms import CompanyForm,DepartmentForm
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
            return redirect('company_detail', pk=new_company.pk)
    else:
        form = CompanyForm()

    return render(request, 'company/company_create.html', {'form': form})


@login_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)

    return render(request, 'company/company_edit.html', {'form': form})
@login_required
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'company/company_list.html', {'companies': companies})

@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    employees = CustomUser.objects.filter(company=company)
    requests = Request.objects.filter(requester__in=employees)
    departments = Department.objects.filter(company=company, parent_department__isnull=True)

    department_form = DepartmentForm()  # Пустая форма для создания отдела
    subdepartment_form = DepartmentForm()  # Пустая форма для создания подотдела

    return render(request, 'company/company_detail.html', {
        'company': company,
        'employees': employees,
        'requests': requests,
        'departments': departments,
        'department_form': department_form,
        'subdepartment_form': subdepartment_form
    })
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