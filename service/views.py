from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Company,Request
from .forms import  CompanyForm
from django.contrib.auth import login
from .forms import CustomUserCreationForm
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
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile/profile.html', {'user_profile': user_profile, 'form': form})

@login_required
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')

    else:
        form = UserProfileForm(instance=user_profile)

    context = {'form': form}
    return render(request, 'profile/edit_profile.html', context)
def request_list(request):
    requests = Request.objects.filter(requester=request.user)
    return render(request, 'requests/request_list.html', {'requests': requests})

@login_required
def create_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.requester = request.user
            new_request.save()
            return redirect('request_list')
    else:
        form = RequestForm()
    return render(request, 'requests/create_request.html', {'form': form})

@login_required
def request_detail(request, pk):
    request_detail = get_object_or_404(Request, pk=pk)
    return render(request, 'requests/request_detail.html', {'request_detail': request_detail})

@login_required
def request_update(request, pk):
    request_instance = get_object_or_404(Request, pk=pk)
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()
            return redirect('request_detail', pk=pk)
    else:
        form = RequestForm(instance=request_instance)
    return render(request, 'requests/request_update.html', {'form': form})