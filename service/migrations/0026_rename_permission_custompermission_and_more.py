# Generated by Django 4.2.5 on 2023-11-25 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0025_grouppermission_remove_customuser_role_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Permission',
            new_name='CustomPermission',
        ),
        migrations.RenameField(
            model_name='grouppermission',
            old_name='permission',
            new_name='custompermission',
        ),
    ]
