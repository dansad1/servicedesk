from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from service.forms.User_forms import CustomUserCreationForm, User  # Assuming you have this form
from service.models import CustomUser
from service.forms.User_forms import CustomLoginForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

# Создание нового пользователя
@login_required
def create_user_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # Replace with your user list view name
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'user/create_user.html', context)

# Вывод списка пользователей
@login_required
def user_list(request):
    # Check if the user is in the Administrator group
    if request.user.is_superuser:
        users = CustomUser.objects.all()
        return render(request, 'user/user_list.html', {'users': users})
    else:
        return redirect('profile')
    

@login_required
def user_delete(request):
    if request.method == 'POST':
        user_ids = request.POST.getlist('selected_users')
        if user_ids:
            CustomUser.objects.filter(id__in=user_ids).delete()
            messages.success(request, 'Выбранные пользователи были удалены.')
        else:
            messages.warning(request, 'Пожалуйста, выберите хотя бы одного пользователя для удаления.')
    return redirect('user_list')


class CustomLoginView(auth_views.LoginView):
    form_class = CustomLoginForm
    template_name = 'registration/login.html'
    
    def get_success_url(self) -> str:
        return reverse_lazy('home')