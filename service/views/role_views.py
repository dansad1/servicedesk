from django.shortcuts import render, redirect
from ..models import Role,Permission
from ..forms import   RoleForm
from ..permissions import *
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'roles/role_list.html', {'roles': roles})

def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            for permission in Permission.objects.all():
                access_level = form.cleaned_data.get(f'access_level_{permission.pk}')
                if access_level:
                    return redirect('role_list')
                else:
                    form = RoleForm()
                return render(request, 'roles/role_create.html', {'form': form})
def role_edit(request, pk):
    role = Role.objects.get(pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if form.is_valid():
        form.save()
        return redirect('role_list')
    return render(request, 'roles/role_create.html', {'form': form})

def role_delete(request, pk):
    role = Role.objects.get(pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('role_list')
    return render(request, 'roles/role_confirm_delete.html', {'role': role})
