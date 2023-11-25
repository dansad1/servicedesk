from django.core.checks import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group
from ..forms  import GroupForm
from ..models import GroupPermission, CustomPermission


def role_create_or_edit(request, group_id=None):
    group = get_object_or_404(Group, id=group_id) if group_id else None
    form = GroupForm(request.POST or None, instance=group)

    # Создаем словарь для отображения текущих уровней доступа
    current_access_levels = {}
    if group:
        for gp in GroupPermission.objects.filter(group=group):
            current_access_levels[gp.custompermission.id] = gp.access_level

    if request.method == 'POST' and form.is_valid():
        saved_group = form.save()

        # Очистка существующих разрешений для группы
        GroupPermission.objects.filter(group=saved_group).delete()

        # Создание новых связей GroupPermission для action_permissions
        for permission in form.cleaned_data['action_permissions']:
            access_level = request.POST.get(f'access_level_{permission.id}', 'personal')
            GroupPermission.objects.create(
                group=saved_group,
                custompermission=permission,
                access_level=access_level
            )

        # Обработка section_permissions (без уровней доступа)
        for section_permission in form.cleaned_data['section_permissions']:
            GroupPermission.objects.create(
                group=saved_group,
                custompermission=section_permission
            )

        return redirect('role_list')

    # Словарь для отображения уровней доступа в шаблоне
    access_levels_info = {
        permission.id: permission.requires_access_level for permission in CustomPermission.objects.filter(code_name__startswith='action_')
    }

    context = {
        'form': form,
        'access_levels_info': access_levels_info,
        'current_access_levels': current_access_levels,
    }
    return render(request, 'role/role_create_edit.html', context)

def role_list(request):
    groups = Group.objects.all()
    return render(request, 'role/role_list.html', {'groups': groups})
def role_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    messages.success(request, "Role successfully deleted.")
    return redirect('role_list')
