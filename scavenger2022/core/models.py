from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass


class QrCode(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    location = models.CharField(max_length=100)
    users = models.ManyToManyField(
        User, related_name="qr_scanned"
    )

    def __str__(self):
        return self.id


class Hint(models.Model):
    qr_code = models.ForeignKey(QrCode, on_delete=models.CASCADE)
    hint = models.CharField(max_length=100)

    def __str__(self):
        return self.qr_code

