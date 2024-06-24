from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group, Permission
from service.forms.Role_forms import *


def role_create(request, group_id=None):
    group = get_object_or_404(Group, id=group_id) if group_id else None

    if request.method == "POST":
        group_form = GroupForm(request.POST, instance=group)
        if group_form.is_valid():
            group = group_form.save()
            GroupPermission.objects.filter(group=group).delete()  # Clear existing permissions
            permissions = request.POST.getlist('custompermission')
            for permission_id in permissions:
                access_level = request.POST.get(f'access_level_{permission_id}', 'personal')
                custom_permission = CustomPermission.objects.get(id=permission_id)
                GroupPermission.objects.create(group=group, custompermission=custom_permission, access_level=access_level)
            return redirect('role_list')
    else:
        group_form = GroupForm(instance=group)
        permission_form = GroupPermissionForm()

    return render(request, 'role/role_create_edit.html', {
        'group_form': group_form,
        'permission_form': permission_form,
        'group': group,
        'access_levels_choices': GroupPermission.ACCESS_LEVEL_CHOICES
    })

def role_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        group_form = GroupForm(request.POST, instance=group)
        if group_form.is_valid():
            group = group_form.save()
            GroupPermission.objects.filter(group=group).delete()
            permissions = request.POST.getlist('custompermission')
            for permission_id in permissions:
                access_level = request.POST.get(f'access_level_{permission_id}', 'personal')
                custom_permission = CustomPermission.objects.get(id=permission_id)
                GroupPermission.objects.create(group=group, custompermission=custom_permission, access_level=access_level)
            return redirect('role_list')
    else:
        group_form = GroupForm(instance=group)
        permission_form = GroupPermissionForm()

    return render(request, 'role/role_create_edit.html', {
        'group_form': group_form,
        'permission_form': permission_form,
        'group': group,
        'access_levels_choices': GroupPermission.ACCESS_LEVEL_CHOICES
    })
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