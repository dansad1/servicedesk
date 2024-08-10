from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group, Permission
from service.forms.Role_forms import GroupPermissionForm, GroupForm
from service.models import CustomPermission, GroupPermission


def role_list(request):
    groups = Group.objects.all()
    return render(request, 'role/role_list.html', {'groups': groups})

def role_create(request):
    permissions = CustomPermission.objects.all()
    if request.method == "POST":
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            group = group_form.save()
            update_group_permissions(group, request.POST)
            messages.success(request, 'Роль успешно создана.')
            return redirect('role_list')
    else:
        group_form = GroupForm()

    return render(request, 'role/role_create_edit.html', {
        'group_form': group_form,
        'permissions': permissions,
        'current_permissions': {}
    })

def role_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    permissions = CustomPermission.objects.all()
    current_permissions = {
        permission.custompermission_id: permission.access_level
        for permission in GroupPermission.objects.filter(group=group)
    }

    # Подготовка данных для шаблона
    permissions_with_levels = []
    for permission in permissions:
        permissions_with_levels.append({
            'permission': permission,
            'access_level': current_permissions.get(permission.id, 'personal'),
            'checked': permission.id in current_permissions
        })

    if request.method == 'POST':
        group_form = GroupForm(request.POST, instance=group)
        if group_form.is_valid():
            group = group_form.save()
            update_group_permissions(group, request.POST)
            messages.success(request, 'Роль успешно обновлена.')
            return redirect('role_list')
    else:
        group_form = GroupForm(instance=group)

    return render(request, 'role/role_create_edit.html', {
        'group_form': group_form,
        'permissions_with_levels': permissions_with_levels,
        'group': group,
    })

def role_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    messages.success(request, "Роль успешно удалена.")
    return redirect('role_list')

def update_group_permissions(group, post_data):
    permissions = CustomPermission.objects.all()
    GroupPermission.objects.filter(group=group).delete()
    for permission in permissions:
        if str(permission.id) in post_data.getlist('permissions[]'):
            access_level = post_data.get(f'access_level_{permission.id}', 'personal')
            GroupPermission.objects.create(
                group=group,
                custompermission=permission,
                access_level=access_level
            )
