from django.contrib.auth.models import AbstractUser
from django.db import models
<<<<<<< HEAD
=======

>>>>>>> 9eed3de62b1ad86786086ac57fd0d42cfda51453

class User(AbstractUser):
    metropolis_id = models.IntegerField()
    refresh_token = models.CharField(max_length=128)


class QrCode(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    location = models.CharField(max_length=100)
    users = models.ManyToManyField(
        User, related_name="qr_scanned"
    )

    def __str__(self):
        return self.id


class Hint(models.Model):
<<<<<<< HEAD
=======
    id = models.AutoField(primary_key=True)
>>>>>>> 9eed3de62b1ad86786086ac57fd0d42cfda51453
    qr_code = models.ForeignKey(QrCode, on_delete=models.CASCADE)
    hint = models.CharField(max_length=100)

    def __str__(self):
<<<<<<< HEAD
        return self.qr_code

=======
        return self.id
>>>>>>> 9eed3de62b1ad86786086ac57fd0d42cfda51453
