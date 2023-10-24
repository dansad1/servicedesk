from ..models import CustomUser
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..permissions import can_edit_user_list
@login_required
def user_list(request):
    # Check if the user is in the Administrator group
    if request.user.groups.filter(name='Администратор').exists():
        users = CustomUser.objects.all()
        return render(request, 'user/user_list.html', {'users': users})
    else:
        return redirect('profile')