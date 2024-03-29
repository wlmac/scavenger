# Generated by Django 4.1.4 on 2023-01-08 03:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_alter_user_team"),
    ]

    operations = [
        migrations.AddField(
            model_name="qrcode",
            name="image_url",
            field=models.URLField(
                blank=True,
                help_text="A URL to an image of where the QR code is located (try imgur)",
            ),
        ),
    ]
