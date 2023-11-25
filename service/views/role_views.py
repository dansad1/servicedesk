from django.core.checks import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group, Permission
from ..forms  import GroupForm
from ..models import GroupPermission


def role_create_or_edit(request, group_id=None):
    group = get_object_or_404(Group, id=group_id) if group_id else None
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            saved_group = form.save()
            # Очистите существующие связи GroupPermission
            GroupPermission.objects.filter(group=saved_group).delete()
            # Создание новых связей GroupPermission
            for permission in form.cleaned_data['custompermissions']:
                GroupPermission.objects.create(
                    group=saved_group,
                    permission=permission,
                    access_level=form.cleaned_data['access_levels']
                )
            return redirect('role_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'role/role_create_edit.html', {'form': form})
def role_list(request):
    groups = Group.objects.all()
    return render(request, 'role/role_list.html', {'groups': groups})
def role_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    messages.success(request, "Role successfully deleted.")
    return redirect('role_list')
