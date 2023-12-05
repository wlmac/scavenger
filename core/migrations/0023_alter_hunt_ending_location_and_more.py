# Generated by Django 4.1.13 on 2023-12-05 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0022_remove_hunt_early_access_users_hunt_testers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hunt",
            name="ending_location",
            field=models.ForeignKey(
                blank=True,
                help_text="(Optional) A specified ending location for the hunt. All teams will get as their last location.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ending_location",
                to="core.qrcode",
            ),
        ),
        migrations.AlterField(
            model_name="hunt",
            name="middle_locations",
            field=models.ManyToManyField(
                help_text="Possible locations that are not the start or end",
                related_name="hunt",
                to="core.qrcode",
            ),
        ),
        migrations.AlterField(
            model_name="hunt",
            name="path_length",
            field=models.PositiveSmallIntegerField(
                default=13,
                help_text="Length of the path: The amount of codes each time will have to find before the end. (not including start/end)",
            ),
        ),
        migrations.AlterField(
            model_name="hunt",
            name="starting_location",
            field=models.ForeignKey(
                blank=True,
                help_text="(Optional) A specified starting location for the hunt. All teams will have to scan this QR code as their first.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="starting_location",
                to="core.qrcode",
            ),
        ),
    ]
