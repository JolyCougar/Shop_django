# Generated by Django 5.1.3 on 2024-11-18 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_product_attribute'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='marketing_info',
            field=models.TextField(blank=True, null=True),
        ),
    ]