# Generated by Django 4.2.5 on 2023-11-06 21:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0018_rename_allowed_groups_statustransition_allowed_group'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statustransition',
            old_name='allowed_group',
            new_name='allowed_groups',
        ),
    ]