# Generated by Django 4.2.5 on 2023-10-09 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_customuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='service.company'),
        ),
    ]