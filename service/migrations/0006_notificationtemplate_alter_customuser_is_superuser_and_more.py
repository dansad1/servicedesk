# Generated by Django 5.0.1 on 2024-06-23 10:17

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0005_alter_grouppermission_access_level'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('push', 'Push Notification')], max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('subject', models.CharField(blank=True, max_length=255)),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(help_text='Используйте инструменты редактора для форматирования текста.')),
            ],
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
        migrations.AlterField(
            model_name='grouppermission',
            name='access_level',
            field=models.CharField(blank=True, choices=[('global', 'Global'), ('company', 'Company'), ('department', 'Department'), ('personal', 'Personal')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='status',
            name='color',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]