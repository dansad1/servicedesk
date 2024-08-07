# Generated by Django 5.0.1 on 2024-07-07 16:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0013_remove_notificationsetting_template_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notificationsetting',
            name='email_template',
        ),
        migrations.RemoveField(
            model_name='notificationsetting',
            name='push_template',
        ),
        migrations.RemoveField(
            model_name='notificationsetting',
            name='sms_template',
        ),
        migrations.AddField(
            model_name='notificationsetting',
            name='template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='service.notificationtemplate'),
        ),
    ]
