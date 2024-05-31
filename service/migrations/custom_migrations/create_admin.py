from service.models import CustomUser
from django.contrib.auth.models import Group

def add_admin(apps, schema_editor):
    #CustomUser = apps.get_model('service', 'CustomUser')
    
    
    admin_group, created = Group.objects.get_or_create(name="admin")
    
    superuser = CustomUser(
        username='admin',
        email='sidorov.egor.main@gmail.com',
        first_name='admin',
        last_name='admin',
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )
    
    superuser.set_password("admin")
    
    superuser.group = admin_group
    superuser.save()
