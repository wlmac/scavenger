# Generated by Django 4.1.3 on 2022-12-01 06:32

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_remove_team_members_user_team"),
    ]

    operations = [
        migrations.AddField(
            model_name="qrcode",
            name="short",
            field=models.CharField(
                default="",
                help_text="Short string to remember the place.",
                max_length=64,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="invite",
            name="code",
            field=models.CharField(
                default=core.models.generate_invite_code, max_length=32, unique=True
            ),
        ),
    ]
