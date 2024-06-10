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

            for permission in selected_permissions:
                access_level = permission_form.cleaned_data.get(f'access_level_{permission.id}', 'personal')
                GroupPermission.objects.create(
                    group=role,
                    custompermission=permission,
                    access_level=access_level
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
        permission_form = GroupPermissionForm(request.POST, instance=role)

        if form.is_valid() and permission_form.is_valid():
            role = form.save()
            selected_permissions = permission_form.cleaned_data['custompermission']
            role.permissions.set(selected_permissions)

            for permission in selected_permissions:
                access_level = permission_form.cleaned_data.get(f'access_level_{permission.id}', 'personal')
                GroupPermission.objects.update_or_create(
                    group=role,
                    custompermission=permission,
                    defaults={'access_level': access_level}
                )

            return redirect('role_list')
    else:
        form = GroupForm(instance=role)
        permission_form = GroupPermissionForm(instance=role)

    # Подготовка динамических полей для шаблона
    dynamic_fields = []
    for permission in permission_form.fields['custompermission'].queryset:
        field_name = f'access_level_{permission.id}'
        dynamic_fields.append({
            'permission': permission,
            'field': permission_form[field_name],
            'choices': permission_form.fields[field_name].choices,
            'initial': permission_form.initial.get(field_name, 'personal')
        })

    context = {
        'group_form': form,
        'permission_form': permission_form,
        'dynamic_fields': dynamic_fields,
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
