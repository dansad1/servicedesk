# Generated by Django 4.2.5 on 2023-10-09 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('user', 'Пользователь'), ('admin', 'Администратор')], default='user', max_length=10, verbose_name='Роль'),
        ),
    ]