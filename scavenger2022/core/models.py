from django.contrib.auth.models import AbstractUser
from django.db import models


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
