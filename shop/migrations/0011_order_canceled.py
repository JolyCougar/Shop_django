# Generated by Django 5.1.3 on 2025-01-21 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_order_paid_order_payment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='canceled',
            field=models.BooleanField(default=False),
        ),
    ]
