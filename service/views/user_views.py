from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from service.forms import CustomUserCreationForm  # Assuming you have this form
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