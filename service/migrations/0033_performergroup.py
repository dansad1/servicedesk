# Generated by Django 5.0.1 on 2024-02-05 19:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0032_alter_company_options_company_ceo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformerGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('companies', models.ManyToManyField(related_name='service_groups', to='service.company')),
                ('members', models.ManyToManyField(related_name='performer_groups', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]