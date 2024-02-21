from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from service.models import CustomUser, Company,Request,Status
from service.forms.Company_forms import  CompanyForm
from django.contrib.auth import login
from service.forms.User_forms import CustomUserCreationForm, CustomUserEditForm
from django.urls import reverse_lazy
from  service.forms import *
from django.shortcuts import get_object_or_404
from django.urls import reverse
from service.views import profile_views
from django.contrib.auth.models import Group



# Регистрация пользователя
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

# Домашняя страница
def home(request):
    return render(request, 'pages/home.html')

# Вывод профиля пользователя
@login_required
def profile(request):
    user = request.user
    user_profile = CustomUser.objects.get(username=user.username)
    is_admin = request.user.groups.filter(name='Администратор').exists()  # Исправлено имя группы
    return render(request, 'profile/profile.html', {'user_profile': user_profile, 'is_admin': is_admin})


# Редактирование пользователя
@login_required
def edit_profile(request, pk=None):
    target_user = get_object_or_404(CustomUser, pk=pk) if pk else request.user
    can_edit_profile = request.user.has_perm('service.section_edit_myself', target_user)

    if request.method == 'POST' and can_edit_profile:
        form = CustomUserEditForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserEditForm(instance=target_user)

    return render(request, 'profile/edit_profile.html', {
        'form': form,
        'can_edit_profile': can_edit_profile
    })