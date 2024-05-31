

def add_group_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    CustomPermission = apps.get_model('service', 'CustomPermission')
    GroupPermission = apps.get_model('service', 'GroupPermission')
    
    admin_group, created = Group.objects.get_or_create(name="admin")
    user_group, created = Group.objects.get_or_create(name="user")
    
    all_permissions = CustomPermission.objects.all()
    
    for permission in all_permissions:
        GroupPermission.objects.create(
            group=admin_group,
            custompermission=permission,
            access_level='global'
        )
        
    user_permissions = [
        {'code_name': 'profile_can_edit', 'name': 'Can Edit Profile'},
        {'code_name': 'requests_can_edit', 'name': 'Can Edit Requests'},
        {'code_name': 'requests_can_view', 'name': 'Can View Requests'},
        {'code_name': 'requests_1_can_create', 'name': 'Can Create Requests'}
    ]
    
    for permission in user_permissions:
        custom_permission, created = CustomPermission.objects.get_or_create(
            code_name=permission['code_name'],
            defaults={'name': permission['name']}
        )
        GroupPermission.objects.create(
            group=user_group,
            custompermission=custom_permission,
            access_level='public'
        )