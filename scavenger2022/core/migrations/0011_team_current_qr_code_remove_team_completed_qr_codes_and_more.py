# Generated by Django 4.1.3 on 2022-11-29 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_rename_current_qr_code_team_completed_qr_codes"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="current_qr_code",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name="team",
            name="completed_qr_codes",
        ),
        migrations.AddField(
            model_name="team",
            name="completed_qr_codes",
            field=models.ManyToManyField(
                related_name="completed_qr_codes", to="core.qrcode"
            ),
        ),
    ]
