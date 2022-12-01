import random
import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import format_html
from django.conf import settings


class User(AbstractUser):
    metropolis_id = models.IntegerField()
    refresh_token = models.CharField(max_length=128)
    team = models.ForeignKey(
        "Team", related_name="members", on_delete=models.CASCADE, blank=True, null=True
    )
    chosen = models.BooleanField()


class QrCode(models.Model):
    id = models.AutoField(primary_key=True)
    # code = models.CharField(max_length=32, default=secrets.token_urlsafe(32), unique=True)
    short = models.CharField(
        max_length=64, help_text="Short string to remember the place."
    )
    location = models.CharField(
        max_length=1024,
        help_text="Location of the QR code. Be specific—it's internal",
    )
    notes = models.TextField(
        help_text="Internal notes",
    )

    def __str__(self):
        return self.short or str(self.id)


class Hint(models.Model):
    qr_code = models.ForeignKey(QrCode, related_name="hints", on_delete=models.CASCADE)
    hint = models.CharField(
        max_length=100,
        help_text="Hint for the QR code, create at least two, preferably three",
    )

    def __str__(self):
        return self.hint


class Team(models.Model):
    # owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="teams_ownership") potentially add this later
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)
    is_open = models.BooleanField(
        default=False
    )  # todo use this field to have a club-like page so you can join an open team
    completed_qr_codes = models.ManyToManyField(
        QrCode, related_name="completed_qr_codes", unique=False, blank=True
    )
    completed_qr_codes.short_description = (
        "All the Qr codes that the team has already located "
    )
    current_qr_code = models.IntegerField(null=True, blank=True)

    def next_code(self) -> QrCode:
        qr_codes = list(QrCode.objects.exclude(id__in=self.completed_qr_codes.all()))
        item = random.choice(qr_codes)
        self.current_qr_code = item.id
        return item

    def is_solo(self):
        return self.members.count() == 1

    def is_full(self):
        return self.members.count() >= settings.MAX_TEAM_SIZE

    def join(self, user: User):
        if user in self.members.all():
            return
        if self.is_full():
            raise IndexError("Team is full")
        self.members.add(user)
        self.save()

    def invites(self):
        return Invite.objects.filter(team=self)

    def __str__(self):
        return self.name


def generate_invite_code():
    return secrets.token_urlsafe(24)


class Invite(models.Model):
    invites = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    code = models.CharField(max_length=32, unique=True, default=generate_invite_code)
