from django.db import migrations
from service.migrations.custom_migrations.create_groups import add_group_permissions

class Migration(migrations.Migration):
    
    dependencies = [
        ('service', '0002_add_custom')
    ]
    
    operations = [
        migrations.RunPython(add_group_permissions),
    ]