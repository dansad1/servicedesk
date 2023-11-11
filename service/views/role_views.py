from django.shortcuts import render, redirect
from ..models import Role
from ..forms import   RoleForm

def role_list(request):
    roles = Role.objects.all()
    return render(request, 'roles/role_list.html', {'roles': roles})

def role_create(request):
    form = RoleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('role_list')
    return render(request, 'roles/role_form.html', {'form': form})

def role_update(request, pk):
    role = Role.objects.get(pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if form.is_valid():
        form.save()
        return redirect('role_list')
    return render(request, 'roles/role_form.html', {'form': form})

def role_delete(request, pk):
    role = Role.objects.get(pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('role_list')
    return render(request, 'roles/role_confirm_delete.html', {'role': role})
