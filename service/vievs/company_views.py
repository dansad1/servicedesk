from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Company,Request,Status
from .forms import  CompanyForm
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from  .forms import *
from django.shortcuts import get_object_or_404
from django.urls import reverse

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