# Generated by Django 5.0.1 on 2024-08-23 23:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0022_companyfieldmeta_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyfieldset',
            name='name',
        ),
    ]