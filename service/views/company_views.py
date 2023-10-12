from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from service.forms import CompanyForm
from django.urls import reverse_lazy
from service.models import CustomUser, Company, Request, Status

def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            # Сохранение компании в базе данных
            company = form.save()
            return redirect('profile')  # Перенаправление на страницу профиля после успешного создания компании
    else:
        form = CompanyForm()

    return render(request, 'company/create_company.html', {'form': form})