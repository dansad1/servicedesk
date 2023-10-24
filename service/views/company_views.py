from django.shortcuts import render, redirect
from service.forms import CompanyForm
from django.urls import reverse_lazy
from service.models import CustomUser, Company, Request, Status
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from ..permissions import can_create_company
from django.shortcuts import get_object_or_404

@login_required
@user_passes_test(can_create_company, login_url='/not-authorized/')  # Use the can_create_company function
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
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    employees = CustomUser.objects.filter(company=company)
    requests = Request.objects.filter(requester__in=employees)

    return render(request, 'company/company_detail.html', {
        'company': company,
        'employees': employees,
        'requests': requests
    })
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

