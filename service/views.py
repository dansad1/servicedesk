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
def request_list(request):
    user = request.user
    requests = Request.objects.filter(company=user.company)
    return render(request, 'request/request_list.html', {'requests': requests})

@login_required
def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.requester = request.user
            new_request.status = Status.objects.get(name='Открыта')  # Set the default status to "Открыта"
            new_request.save()
            return redirect('request_list')
    else:
        form = RequestForm()

    return render(request, 'request/request_create.html', {'form': form})

@login_required
def request_detail(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    user = request.user

    # Проверяем, является ли пользователь создателем, исполнителем или администратором заявки
    is_creator = request_instance.requester == user
    is_assignee = request_instance.assignee == user
    is_admin = user.is_staff

    # Если пользователь соответствует одному из условий, перенаправляем на страницу редактирования с передачей параметра pk
    if is_creator or is_assignee or is_admin:
        url = reverse('request_update', args=[pk])
        return redirect(url)

    # Иначе, отображаем страницу деталей заявки
    return render(request, 'request/request_detail.html', {'request_instance': request_instance})


def request_update(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    user = request.user

    if request.method == 'POST':
        form = RequestForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()

            # Check if an assignee has been added to the request
            if request_instance.assignee:
                status_in_work, created = Status.objects.get_or_create(name="В работе")
                request_instance.status = status_in_work
            else:
                status_opened, created = Status.objects.get_or_create(name="Открыта")
                request_instance.status = status_opened

            # Check if the "completed" checkbox is checked
            is_completed = form.cleaned_data.get('completed', False)
            if is_completed:
                status_completed, created = Status.objects.get_or_create(name="Выполнена")
                request_instance.status = status_completed

            request_instance.save()

            return redirect('request_detail', pk=pk)
    else:
        form = RequestForm(instance=request_instance)

    return render(request, 'request/request_update.html', {'form': form, 'request_instance': request_instance})


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