# Generated by Django 4.1.13 on 2023-12-10 02:45

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


def clear_teams(apps, schema_editor):
    Team = apps.get_model("core", "team")
    Team.objects.all().delete()  # delete all teams IRREVERSIBLE


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0020_alter_logicpuzzlehint_qr_index_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="hint",
            options={},
        ),
        migrations.AddField(
            model_name="qrcode",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="TeamMembership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.team"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "team")},
            },
        ),
        migrations.RunPython(
            clear_teams, reverse_code=None
        ),  # if you want to "reverse" change this to migrations.RunPython.noop though it will not bring back the teams
        migrations.RemoveField(model_name="team", name="members"),  # added manually
        migrations.AddField(  # changed from alter to add
            model_name="team",
            name="members",
            field=models.ManyToManyField(
                related_name="teams",
                related_query_name="teams",
                through="core.TeamMembership",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
