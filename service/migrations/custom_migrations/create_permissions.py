

def create_permissions(apps, schema_editor):
    CustomPermission = apps.get_model('service', "CustomPermission")
    
    # Полномочия для заявок
    CustomPermission.objects.create(code_name="requests_1_can_create", name="Создавать заявки")
    CustomPermission.objects.create(code_name="requests_1_can_delete", name="Удалять заявки")

    CustomPermission.objects.create(code_name="requests_view_personal", name="Просматривать свои заявки")
    CustomPermission.objects.create(code_name="requests_view_department", name="Просматривать заявки своего отдела")
    CustomPermission.objects.create(code_name="requests_view_department_with_subs",
                                    name="Просматривать заявки своего отдела с дочерними")
    CustomPermission.objects.create(code_name="requests_view_company", name="Просматривать заявки своей компании")
    CustomPermission.objects.create(code_name="requests_view_global", name="Просматривать все заявки")

    # Редактирование заявок
    CustomPermission.objects.create(code_name="requests_edit_personal", name="Редактировать свои заявки")
    CustomPermission.objects.create(code_name="requests_edit_department", name="Редактировать заявки своего отдела")
    CustomPermission.objects.create(code_name="requests_edit_department_with_subs",
                                    name="Редактировать заявки своего отдела с дочерними")
    CustomPermission.objects.create(code_name="requests_edit_company", name="Редактировать заявки своей компании")
    CustomPermission.objects.create(code_name="requests_edit_global", name="Редактировать все заявки")

    # Назначать исполнителей
    CustomPermission.objects.create(code_name="requests_can_add_executors", name="Назначать исполнителей и группы исполнителей")
    
    # Полномочия по пользователям/группам пользователей
    CustomPermission.objects.create(code_name="users_can_create", name="Создавать пользователей и группы исполнителей")
    CustomPermission.objects.create(code_name="users_can_edit", name="Редактировать пользователей и группы исполнителей")
    CustomPermission.objects.create(code_name="users_can_delete", name="Удалять пользователей и группы исполнителей")
    
    # Полномочия по компаниям
    CustomPermission.objects.create(code_name="companies_can_create", name="Создавать компании")
    CustomPermission.objects.create(code_name="companies_can_edit", name="Редактировать компании")
    CustomPermission.objects.create(code_name="companies_can_delete", name="Удалять компании")
    
    # Полномочия по отделам
    CustomPermission.objects.create(code_name="departments_can_create", name="Создавать отделы")
    CustomPermission.objects.create(code_name="departments_can_edit", name="Редактировать отделы")
    CustomPermission.objects.create(code_name="departments_can_delete_", name="Удалять отделы")
    
    # Полномочия по ролям
    CustomPermission.objects.create(code_name="roles_can_create", name="Создавать роли")
    CustomPermission.objects.create(code_name="roles_can_edit", name="Редактировать роли")
    CustomPermission.objects.create(code_name="roles_can_delete", name="Удалять роли")
    
    # Полномочия по активам
    CustomPermission.objects.create(code_name="assets_can_create", name="Создавать активы")
    CustomPermission.objects.create(code_name="assets_can_edit", name="Редактировать активы")
    CustomPermission.objects.create(code_name="assets_can_delete", name="Удалять активы")
    
    CustomPermission.objects.create(code_name="assets_types_can_create", name="Создавать типы активов")
    CustomPermission.objects.create(code_name="assets_types_can_edit", name="Редактировать типы активов")
    CustomPermission.objects.create(code_name="assets_types_can_delete", name="Удалять типы активов")
    
    CustomPermission.objects.create(code_name="assets_types_attr_can_create", name="Создавать атрибуты")
    
    # Полномочия по профилю 
    CustomPermission.objects.create(code_name="profile_can_edit", name="Редактировать свой профиль")
    
    # Полномочия по настройкам
    CustomPermission.objects.create(code_name="settings_requests_types_can_create", name="Создавать типы заявок")
    CustomPermission.objects.create(code_name="settings_requests_types_can_edit", name="Редактировать типы заявок")
    CustomPermission.objects.create(code_name="settings_requests_types_can_delete", name="Удалять типы заявок")
    
    CustomPermission.objects.create(code_name="settings_requests_priority_can_create", name="Создавать приоритеты заявок")
    CustomPermission.objects.create(code_name="settings_requests_priority_can_edit", name="Редактировать приоритеты заявок")
    CustomPermission.objects.create(code_name="settings_requests_priority_can_delete", name="Удалять типы заявок")
    
    CustomPermission.objects.create(code_name="settings_status_list_can_create", name="Создавать списки статусов")
    CustomPermission.objects.create(code_name="settings_status_list_can_edit", name="Редактировать списки статусов")
    CustomPermission.objects.create(code_name="settings_status_list_can_delete", name="Удалять списки статусов")
    
    CustomPermission.objects.create(code_name="settings_status_trans_can_create", name="Создавать переходы статусов")
    #CustomPermission.objects.create(code_name="can_edit_status_trans", name="Can Edit Status List")
    CustomPermission.objects.create(code_name="settings_status_tran_can_delete", name="Удалять переходы статусов")
    
    CustomPermission.objects.create(code_name="settings_smtp_can_show", name="Показывать настройки SMTP")
    
    
    CustomPermission.objects.create(code_name="settings_docs_can_show", name="Показывать списки документов")
    CustomPermission.objects.create(code_name="settings_docs_can_download", name="Загружать документы")
    
    CustomPermission.objects.create(code_name="settings_notifications_can_show", name="Показывать обзор уведомлений")
    
    # Полномочия по интерфейсу
    CustomPermission.objects.create(code_name="interface_can_view_assets", name='Показывать раздел "Список заявок"')
    CustomPermission.objects.create(code_name="interface_can_view_actives", name='Показывать раздел "Список активов"')
    CustomPermission.objects.create(code_name="interface_can_view_settings", name='Показывать раздел "Настройки" ')
    CustomPermission.objects.create(code_name="interface_can_view_chat", name='Показывать раздел "Чат"')
    CustomPermission.objects.create(code_name="interface_can_view_companies", name='Показывать раздел "Список компаний"')
    CustomPermission.objects.create(code_name="interface_can_view_users", name='Показывать раздел "Списко пользователей"')
    CustomPermission.objects.create(code_name="interface_can_view_roles", name='Показывать раздел "Управление ролями"')
    
    
    
    
    
    