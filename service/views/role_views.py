from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group, Permission
from ..models import GroupPermission, CustomPermission
from service.forms.Role_forms import *



# Создание роли 
def role_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            print(form.data)
            new_group = form.save()
            # Сохранение уровней доступа для каждого разрешения действий
            for permission in form.cleaned_data['action_permissions']:
                access_level = request.POST.get(f'access_level_{permission.id}', 'personal')
                GroupPermission.objects.create(
                    group=new_group,
                    custompermission=permission,
                    access_level=access_level
                )
            # Сохранение разрешений для разделов
            for section_permission in form.cleaned_data['section_permissions']:
                GroupPermission.objects.create(
                    group=new_group,
                    custompermission=section_permission
                )
            return redirect('role_list')
    else:
        existing_group_id = request.GET.get('group_id')  # Assuming you pass the group_id in the request
        existing_group = get_object_or_404(Group, id=existing_group_id) if existing_group_id else None
        print(existing_group_id)
        # Pass the existing Group instance to the form
        form = GroupForm(instance=existing_group)
    print(request.method)
    print(form.data)
    print(request.user.get_user_permissions())
    print("__________________________")
    print(request.user.get_group_permissions())
    return render(request, 'role/role_create_edit.html', {'form': form})



# Редактирование роли
def role_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    print(group)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            # Удаление старых разрешений перед сохранением новых
            GroupPermission.objects.filter(group=group).delete()
            # Сохранение новых уровней доступа
            for permission in form.cleaned_data['action_permissions']:
                access_level = request.POST.get(f'access_level_{permission.id}', 'personal')
                GroupPermission.objects.create(
                    group=group,
                    custompermission=permission,
                    access_level=access_level
                )
            # Сохранение новых разрешений для разделов
            for section_permission in form.cleaned_data['section_permissions']:
                GroupPermission.objects.create(
                    group=group,
                    custompermission=section_permission
                )
            return redirect('role_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'role/role_create_edit.html', {'form': form, 'group': group})



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
