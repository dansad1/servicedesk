from django.shortcuts import render, redirect

from .forms import PermissionCreationForm
from .models import Permission
from .constraints import ACTIONS,ENTITIES,DEPARTMENT_LEVELS

def create_permission(request):
    if request.method == 'POST':
        form = PermissionCreationForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            entity = form.cleaned_data['entity']
            level = form.cleaned_data['level']

            # Создание нового разрешения
            code_name = f"{action}_{entity}_{level}"
            human_readable_name = f"{action.capitalize()} {entity.replace('_', ' ')} at {level} level"
            Permission.objects.create(code_name=code_name, name=human_readable_name)

            return redirect('profile')  # Перенаправление после создания

    else:
        form = PermissionCreationForm()

    return render(request, 'permissions.html', {'form': form})
