from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group, Permission
from service.forms.Role_forms import *


def role_create(request, group_id=None):
    if group_id:
        group = get_object_or_404(Group, id=group_id)
    else:
        group = None

    if request.method == "POST":
        group_form = GroupForm(request.POST, instance=group)
        permission_form = GroupPermissionForm(request.POST)

        print("POST data:", request.POST)

        if group_form.is_valid():
            group = group_form.save()
            permissions = request.POST.getlist('permissions[]')

            for permission in permissions:
                access_level_field_name = f'access_level_{permission}'
                access_level = request.POST.get(access_level_field_name)
                custompermission = CustomPermission.objects.get(id=permission)
                if access_level == None:
                    access_level = 'personal'
                GroupPermission.objects.create(
                    group=group,
                    custompermission=custompermission,
                    access_level=access_level
                )
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


# Редактирование роли
def role_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        group_form = GroupForm(request.POST, instance=group)
        permission_form = GroupPermissionForm(request.POST)

        if group_form.is_valid():
            group = group_form.save()

            # Удаление старых разрешений перед сохранением новых
            GroupPermission.objects.filter(group=group).delete()

            permissions = request.POST.getlist('permissions[]')

            for permission_id in permissions:
                try:
                    custompermission = CustomPermission.objects.get(id=permission_id)
                    access_level_field_name = f'access_level_{custompermission.id}'
                    access_level = request.POST.get(access_level_field_name, 'personal')

                    GroupPermission.objects.create(
                        group=group,
                        custompermission=custompermission,
                        access_level=access_level
                    )
                except CustomPermission.DoesNotExist:
                    # Обработка случая, если разрешение не найдено
                    # logger.warning(f"Permission with id {permission_id} does not exist.")
                    continue

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