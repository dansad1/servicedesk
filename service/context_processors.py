from .models import GroupPermission

def user_permissions(request):
    if request.user.is_authenticated:
        permissions = set(GroupPermission.objects.filter(
            group=request.user.group
        ).values_list('custompermission__code_name', flat=True))
    else:
        permissions = set()
    return {'user_permissions': permissions}
