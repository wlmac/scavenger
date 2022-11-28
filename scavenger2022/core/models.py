from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import format_html


class User(AbstractUser):
    metropolis_id = models.IntegerField()
    refresh_token = models.CharField(max_length=128)


class QrCode(models.Model):
    id = models.AutoField(primary_key=True)
    location = models.CharField(
        max_length=100,
        help_text="Location of the QR code, be specific, it's admin only",
    )
    users = models.ManyToManyField(
        User,
        related_name="qr_scanned",
        help_text="Users that have located this QR code",
    )

    def uri(self):
        from django.conf import settings

        return format_html(
            "<a href='{url}'>{url}</a>",
            url=settings.TRUE_URI + "/api/qr/" + str(self.id),
        )

    uri.short_description = "Url that the QR code should point to"

    def __str__(self):
        return str(self.id)


class Hint(models.Model):
    qr_code = models.ForeignKey(QrCode, on_delete=models.CASCADE)
    hint = models.CharField(
        max_length=100,
        help_text="Hint for the QR code, create at least two, preferably three",
    )

    def __str__(self):
        return self.hint
