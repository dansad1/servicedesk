# Generated by Django 4.2.5 on 2023-11-07 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0019_rename_allowed_group_statustransition_allowed_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='uploads/'),
        ),
    ]
