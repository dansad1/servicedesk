# Generated by Django 4.2.5 on 2023-11-14 20:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0023_remove_customuser_role_remove_permission_codename_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='roles',
        ),
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='service.role'),
        ),
    ]
