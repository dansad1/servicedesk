from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from service.models import CustomUser, Company,Request,Status
from service.forms import  CompanyForm
from django.contrib.auth import login
from service.forms import CustomUserCreationForm
from django.urls import reverse_lazy
from  service.forms import *
from django.shortcuts import get_object_or_404
from django.urls import reverse
from service.views import profile_views
from django.contrib.auth.models import Group
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически входить после регистрации
            return redirect('home')  # Замените 'home' на URL вашей домашней страницы
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    return render(request, 'pages/home.html')


@login_required
def profile(request):
    user = request.user
    user_profile = CustomUser.objects.get(username=user.username)
    is_admin = request.user.groups.filter(name='Администратор').exists()  # Исправлено имя группы
    return render(request, 'profile/profile.html', {'user_profile': user_profile, 'is_admin': is_admin})

def edit_profile(request, pk=None):
    if pk:
        if request.user.groups.filter(name='Администратор').exists():
            user = get_object_or_404(CustomUser, pk=pk)
        else:
            return redirect('profile')
    else:
        user = request.user

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, 'profile/edit_profile.html', {'form': form})
