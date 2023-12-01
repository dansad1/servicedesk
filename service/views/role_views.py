from django.core.checks import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group, Permission
from ..forms  import GroupForm
from ..models import GroupPermission, CustomPermission

def role_create_or_edit(request, group_id=None):
    group = get_object_or_404(Group, id=group_id) if group_id else None
    form = GroupForm(request.POST or None, instance=group)

    if request.method == 'POST' and form.is_valid():
        saved_group = form.save()

        # Обновляем или создаем связи GroupPermission для action_permissions
        for permission in form.cleaned_data['action_permissions']:
            access_level = request.POST.get(f'access_level_{permission.id}', 'personal')

            group_permission, created = GroupPermission.objects.get_or_create(
                group=saved_group,
                custompermission=permission
            )
            group_permission.access_level = access_level
            group_permission.save()

        # Аналогично для section_permissions
        for section_permission in form.cleaned_data['section_permissions']:
            group_permission, created = GroupPermission.objects.get_or_create(
                group=saved_group,
                custompermission=section_permission
            )
            if created:
                group_permission.access_level = None
            group_permission.save()

        return redirect('role_list')

    return render(request, 'role/role_create_edit.html', {'form': form})

def role_list(request):
    groups = Group.objects.all()
    return render(request, 'role/role_list.html', {'groups': groups})
def role_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    messages.success(request, "Role successfully deleted.")
    return redirect('role_list')
