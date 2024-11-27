# Generated by Django 5.1.3 on 2024-11-20 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_product_marketing_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discounted_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]