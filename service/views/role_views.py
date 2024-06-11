from django.contrib import messages
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import Group, Permission
from ..models import GroupPermission, CustomPermission
from service.forms.Role_forms import *


def role_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        permission_form = GroupPermissionForm(request.POST)

        if form.is_valid() and permission_form.is_valid():
            role = form.save()
            selected_permissions = permission_form.cleaned_data['custompermission']
            role.permissions.set(selected_permissions)

            GroupPermission.objects.filter(group=role).delete()
            for permission in selected_permissions:
                GroupPermission.objects.create(
                    group=role,
                    custompermission=permission,
                )

            return redirect('role_list')
    else:
        form = GroupForm()
        permission_form = GroupPermissionForm()

    context = {
        'group_form': form,
        'permission_form': permission_form,
    }
    return render(request, 'role/role_create.html', context)

def role_edit(request, role_id):
    role = get_object_or_404(Group, id=role_id)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=role)
        permission_form = GroupPermissionForm(request.POST)

        if form.is_valid() and permission_form.is_valid():
            role = form.save()
            selected_permissions = permission_form.cleaned_data['custompermission']
            role.permissions.set(selected_permissions)

            GroupPermission.objects.filter(group=role).delete()
            for permission in selected_permissions:
                GroupPermission.objects.create(
                    group=role,
                    custompermission=permission,
                )

            return redirect('role_list')
    else:
        form = GroupForm(instance=role)
        permission_form = GroupPermissionForm(instance=role)

    context = {
        'group_form': form,
        'permission_form': permission_form,
        'role': role,
    }
    return render(request, 'role/role_edit.html', context)
# Вывод списка ролей
def role_list(request):
    groups = Group.objects.all()
    return render(request, 'role/role_list.html', {'groups': groups})

# Удаление ролей
def role_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    messages.success(request, "Role successfully deleted.")
    return redirect('role_list')
