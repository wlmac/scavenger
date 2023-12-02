# Generated by Django 4.1.3 on 2022-12-12 22:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_remove_user_chosen"),
    ]

    operations = [
        migrations.CreateModel(
            name="LogicPuzzleHint",
            fields=[
                (
                    "id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                (
                    "hint",
                    models.TextField(
                        help_text="Hint for the logic puzzle",
                        max_length=1024,
                    ),
                ),
                (
                    "notes",
                    models.TextField(blank=True, help_text="Internal notes"),
                ),
                (
                    "qr_index",
                    models.IntegerField(
                        help_text="The index of the QR code that this hint is for, that is everyone on their nth QR code will get same same hint (starting from 1)",
                        unique=True,
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="qrcode",
            name="notes",
            field=models.TextField(blank=True, help_text="Internal notes"),
        ),
    ]
