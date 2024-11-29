# Generated by Django 5.1.3 on 2024-11-29 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_marketing'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketing',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='marketing',
            name='description_full',
            field=models.TextField(blank=True, db_index=True),
        ),
    ]
