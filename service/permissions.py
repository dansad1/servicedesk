def can_view_request(user, request):
    user_access_level = user.role.view_request_access_level

    if user_access_level == 'global':
        return True  # Глобальный доступ
    if user_access_level == 'company' and user.company == request.company:
        return True  # Доступ на уровне компании
    if user_access_level == 'department' and user.department == request.department:
        return True  # Доступ на уровне отдела
    if user_access_level == 'personal' and user == request.created_by:
        return True  # Личный доступ
    return False  # Нет доступа

def can_edit_request(user, request):
    user_access_level = user.role.edit_request_access_level

    if user_access_level == 'global':
        return True  # Глобальный доступ на редактирование
    if user_access_level == 'company' and user.company == request.company:
        return True  # Доступ на уровне компании для редактирования
    if user_access_level == 'department' and user.department == request.department:
        return True  # Доступ на уровне отдела для редактирования
    if user_access_level == 'personal' and user == request.created_by:
        return True  # Личный доступ на редактирование
    if user == request.assignee:
        return True  # Доступ для исполнителя заявки

    return False  # Нет доступа на редактирование

def can_delete_request(user, request):
    user_access_level = user.role.delete_request_access_level

    if user_access_level == 'global':
        return True  # Глобальный доступ на удаление заявок
    if user_access_level == 'company' and user.company == request.company:
        return True  # Доступ на уровне компании для удаления заявок
    if user_access_level == 'department' and user.department == request.department:
        return True  # Доступ на уровне отдела для удаления заявок
    if user == request.created_by:
        return True  # Пользователь может удалять свои заявки

    return False  # Нет доступа на удаление заявок