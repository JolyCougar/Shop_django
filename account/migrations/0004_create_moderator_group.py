# myapp/migrations/0002_create_moderator_group.py
from django.db import migrations
from django.contrib.auth.models import Group


def create_moderator_group(apps, schema_editor):
    group_name = "Модераторы"
    Group.objects.get_or_create(name=group_name)


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0003_usersubscription'),
    ]

    operations = [
        migrations.RunPython(create_moderator_group),
    ]
