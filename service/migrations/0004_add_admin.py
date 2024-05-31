from django.db import migrations
from service.migrations.custom_migrations.create_admin import add_admin

class Migration(migrations.Migration):
    
    dependencies = [
        ('service', '0003_add_custom_groups')
    ]
    
    operations = [
        migrations.RunPython(add_admin),
    ]