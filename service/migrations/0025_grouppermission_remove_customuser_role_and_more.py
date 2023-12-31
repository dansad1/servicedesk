# Generated by Django 4.2.5 on 2023-11-19 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('service', '0024_remove_customuser_roles_customuser_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_level', models.CharField(choices=[('global', 'Global'), ('company', 'Company'), ('department', 'Department'), ('personal', 'Personal')], max_length=50)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.permission')),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='role',
        ),
        migrations.AddField(
            model_name='customuser',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='auth.group'),
        ),
        migrations.DeleteModel(
            name='Role',
        ),
    ]
