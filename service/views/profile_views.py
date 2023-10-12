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
    # Получите текущего пользователя
    user = request.user

    try:
        # Попробуйте найти объект CustomUser по username или id пользователя
        user_profile = CustomUser.objects.get(username=user.username)
    except CustomUser.DoesNotExist:
        # Обработайте случай, если пользователь не найден
        user_profile = None

    return render(request, 'profile/profile.html', {'user_profile': user_profile})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserCreationForm(instance=user)

    return render(request, 'profile/edit_profile.html', {'form': form})
@login_required
@permission_required('auth.add_user', raise_exception=True)
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # Перенаправьте на страницу списка пользователей после создания
    else:
        form = UserCreationForm()

    return render(request, 'user/create_user.html', {'form': form})
