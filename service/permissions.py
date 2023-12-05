from service.models import GroupPermission


def can_view_request(user, request_instance):
    # Получаем все разрешения группы пользователя для просмотра
    view_permissions = GroupPermission.objects.filter(
        group=user.group,
        custompermission__code_name='action_view_request'
    )

    # Проверяем каждое разрешение на соответствие условиям
    for perm in view_permissions:
        if perm.access_level == 'global':
            return True
        elif perm.access_level == 'company' and user.company == request_instance.company:
            return True
        elif perm.access_level == 'department' and user.department == request_instance.department:
            return True
        elif perm.access_level == 'personal' and user == request_instance.created_by:
            return True

    return False

def can_edit_request(user, request_instance):
    # Получаем все разрешения группы пользователя для редактирования
    edit_permissions = GroupPermission.objects.filter(
        group=user.group,
        custompermission__code_name='action_edit_request'
    )

    # Проверяем каждое разрешение на соответствие условиям
    for perm in edit_permissions:
        if perm.access_level == 'global':
            return True
        elif perm.access_level == 'company' and user.company == request_instance.company:
            return True
        elif perm.access_level == 'department' and user.department == request_instance.department:
            return True
        elif perm.access_level == 'personal' and user == request_instance.created_by:
            return True

    return False