# Generated by Django 5.1.5 on 2025-03-03 23:43

import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_groupchatroom_room_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupchatroom',
            name='room_code',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=25, unique=True),
        ),
        migrations.AlterField(
            model_name='privatechatroom',
            name='room_code',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=15, unique=True),
        ),
    ]
