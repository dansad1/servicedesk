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


def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(instance=company, company_id=company.pk)
    employees = company.customuser_set.all()
    company_requests = Request.objects.filter(requester__in=employees).select_related('requester', 'assignee', 'status', 'priority', 'request_type')
    departments = company.departments.all()
    subdepartments = Department.objects.filter(parent__company=company).select_related('parent')

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
        'departments': departments,
        'subdepartments': subdepartments,
    }
    return render(request, 'company/company_edit.html', context)
@login_required
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'company/company_list.html', {'companies': companies})
@require_http_methods(["POST"])
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company.delete()
    messages.success(request, "Компания успешно удалена.")
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
        # Проверьте, что это место кода выполняется и queryset устанавливается правильно
        form.fields['users'].queryset = CustomUser.objects.filter(company=company)

    context = {'form': form, 'company': company}
    return render(request, 'company/department_create.html', context)

@login_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department_requests = Request.objects.filter(requester__department=department)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department, company_id=department.company_id)
        if form.is_valid():
            department = form.save()  # Сохраняем объект модели и связанные данные многие-ко-многим
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
    # Redirect to the company edit page
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
