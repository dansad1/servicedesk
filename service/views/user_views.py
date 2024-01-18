from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from service.forms import CustomUserCreationForm, User  # Assuming you have this form
from service.models import CustomUser

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
@login_required
def user_list(request):
    # Check if the user is in the Administrator group
    if request.user.groups.filter(name='Администратор').exists():
        users = CustomUser.objects.all()
        return render(request, 'user/user_list.html', {'users': users})
    else:
        return redirect('profile')
@login_required
@require_POST  # Убедитесь, что запрос на удаление выполняется через POST
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, "Пользователь успешно удален.")
    return redirect('user_list')