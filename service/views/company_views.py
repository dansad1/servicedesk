from django.shortcuts import render, redirect
from service.forms import CompanyForm
from django.urls import reverse_lazy
from service.models import CustomUser, Company, Request, Status
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from ..permissions import can_create_company
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
