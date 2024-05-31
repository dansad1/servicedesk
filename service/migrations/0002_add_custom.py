from django.db import migrations
from service.migrations.custom_migrations.create_admin import add_admin
from service.migrations.custom_migrations.create_permissions import create_permissions
from service.migrations.custom_migrations.create_groups import add_group_permissions

class Migration(migrations.Migration):
    
    dependencies = [
        ('service', '0001_initial')
    ]
    
    operations = [
        migrations.RunPython(create_permissions),
    ]