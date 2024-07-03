from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group, Permission
from service.forms.Role_forms import GroupPermissionForm, GroupForm
from service.models import CustomPermission, GroupPermission


def role_create(request):
    if request.method == "POST":
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            group = group_form.save()
            update_group_permissions(group, request.POST)
            return redirect('role_list')
    else:
        group_form = GroupForm()

    return render(request, 'role/role_create_edit.html', {
        'group_form': group_form,
    })

def role_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.method == 'POST':
        group_form = GroupForm(request.POST, instance=group)
        if group_form.is_valid():
            group = group_form.save()
            update_group_permissions(group, request.POST)
            return redirect('role_list')
    else:
        group_form = GroupForm(instance=group)

    return render(request, 'role/role_create_edit.html', {
        'group_form': group_form,
        'group': group,
    })

def update_group_permissions(group, post_data):
    permissions = post_data.getlist('custompermission')
    GroupPermission.objects.filter(group=group).exclude(custompermission_id__in=permissions).delete()
    for permission_id in permissions:
        access_level = post_data.get(f'access_level_{permission_id}', 'personal')
        custom_permission = CustomPermission.objects.get(id=permission_id)
        group_permission, created = GroupPermission.objects.get_or_create(
            group=group,
            custompermission=custom_permission,
            defaults={'access_level': access_level}
        )
        if not created:
            group_permission.access_level = access_level
            group_permission.save()
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