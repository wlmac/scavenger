# Generated by Django 4.1.4 on 2022-12-10 22:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_alter_hint_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="chosen",
        ),
    ]
