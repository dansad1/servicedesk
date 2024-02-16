# Generated by Django 5.0.1 on 2024-02-13 16:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0034_assettype_asset_attribute_assetattribute'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='name',
            field=models.CharField(default='Default Name', max_length=255),
        ),
        migrations.AlterField(
            model_name='asset',
            name='asset_types',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='service.assettype'),
        ),
        migrations.AlterField(
            model_name='assetattribute',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_attributes', to='service.asset'),
        ),
        migrations.AlterField(
            model_name='assetattribute',
            name='value_asset_reference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referenced_by', to='service.asset'),
        ),
        migrations.AlterField(
            model_name='assetattribute',
            name='value_attribute_reference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referenced_attributes', to='service.assetattribute'),
        ),
    ]
