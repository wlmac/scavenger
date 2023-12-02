from __future__ import annotations

import random
import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import format_html


def generate_invite_code():
    return secrets.token_hex(4)


class User(AbstractUser):
    metropolis_id = models.IntegerField()
    refresh_token = models.CharField(max_length=128)
    team = models.ForeignKey(
        "Team",
        related_name="members",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    @property
    def in_team(self) -> bool:
        try:
            _ = self.team.solo
            return True
        except AttributeError:
            return False


def generate_hint_key():
    return secrets.token_urlsafe(48)


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
    notes = models.TextField(help_text="Internal notes", blank=True)
    key = models.CharField(
        max_length=64,
        unique=True,
        default=generate_hint_key,
        help_text="Key to access the hint, used in the QR code ",
    )
    image_url = models.URLField(
        help_text="A URL to an image of where the QR code is located (try imgur)",
        blank=True,
    )

    def image_tag(self):
        from django.utils.html import escape

        if self.image_url:
            return format_html('<img src="%s" />' % escape(self.image_url))

    image_tag.short_description = "QR Image"
    image_tag.allow_tags = True

    def __str__(self):
        return f"{self.id} {self.short or self.location}"

    @classmethod
    def codes(cls, team: "Team"):
        pks = QrCode.code_pks(team)
        return [QrCode.objects.get(id=a) for a in pks]

    @classmethod
    def code_pks(cls, team: "Team"):
        r = random.Random(team.id)
        pks = [a["pk"] for a in QrCode.objects.all().values("pk")]
        pks = pks[: settings.PATH_LENGTH]
        r.shuffle(pks)
        if isinstance((pk := settings.ALWAYS_LAST_QR_PK), int):
            i = pks.index(pk) if pk in pks else r.randrange(0, len(pks))
            pks = pks[:i] + pks[i + 1 :] + [pk]
        if isinstance((pk := settings.ALWAYS_FIRST_QR_PK), int):
            i = pks.index(pk) if pk in pks else r.randrange(0, len(pks))
            pks = [pk] + pks[:i] + pks[i + 1 :]
        return pks

    def hint(self, team: "Team"):
        r = random.Random(team.id)
        pks = list(self.hints.values("pk"))
        if len(pks) == 0:
            raise TypeError(f"{self} has no hints")
        # TODO: check if seed of team.id and self.id is ok
        for _ in range(
            self.id
        ):  # todo make not O(n) as we have to loop through all hints to keep random state intact. (please note it really only iterates like 20-30 times at max so it doesn't rly matter )
            r.random()
        return Hint.objects.get(id=r.choice(pks)["pk"])


class Hint(models.Model):
    qr_code = models.ForeignKey(QrCode, related_name="hints", on_delete=models.CASCADE)
    hint = models.TextField(
        max_length=1024,
        help_text="Hint for the QR code, create at least two, preferably three",
    )

    def __str__(self):
        return self.hint

    class Meta:
        permissions = [("view_before_start", "Play game before start")]


class Team(models.Model):
    """note, a user can currently be in multiple teams, in the future limit this to one per (class: Hunt)"""

    # owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="teams_ownership") potentially add this later
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True, null=True)
    is_active = models.BooleanField(default=True)
    is_open = models.BooleanField(
        default=False
    )  # todo use this field to have a club-like page so you can join an open team (future feature)
    current_qr_i = models.IntegerField(default=0)
    solo = models.BooleanField(default=False)
    hunt = models.ForeignKey("Hunt", on_delete=models.CASCADE, related_name="teams")

    def update_current_qr_i(self, i: int):
        self.current_qr_i = max(self.current_qr_i, i)
        self.save()

    @property
    def members(self):
        """Returns all members of the team, it's  a related manager so to convert to queryset use .all() or filter it."""
        return User.objects.filter(team=str(self.id))

    @property
    def is_full(self):
        return self.members.count() >= settings.MAX_TEAM_SIZE

    def join(self, user: User):
        if user in self.members.all():
            return
        if self.is_full:
            raise IndexError("Team is full")
        user.team = self
        user.save()

    def invites(self):
        return Invite.objects.filter(team=self)

    @property
    def qr_len(self):
        """Amount of codes the team has completed  (+1) (assuming no skips)"""
        return int(self.current_qr_i) + 1

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self._state.adding:  # only generate key on creation not on update
            Invite.objects.create(team=self, code=generate_invite_code()).save()
        return super().save(*args, **kwargs)


class Invite(models.Model):
    invites = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invites")
    code = models.CharField(max_length=32, unique=True)


class Hunt(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    start = models.DateTimeField()
    end = models.DateTimeField()
    team_size = models.PositiveSmallIntegerField(default=4, help_text="Max Team size")
    path_length = models.PositiveSmallIntegerField(default=15, help_text="Length of the path: The amount of codes each time will have to find before the end.")
    starting_location = models.ForeignKey(
        QrCode, on_delete=models.PROTECT, related_name="starting_location"
    )
    ending_location = models.ForeignKey(
        QrCode, on_delete=models.PROTECT, related_name="ending_location"
    )
    early_access_users = models.ManyToManyField(
        User,
        related_name="early_access_users",
        help_text="Users that can access this hunt before it starts",
    )
    form_url = models.URLField(help_text="Google form to fill out after the hunt", null=True, blank=True)
    ending_text = models.TextField(
        help_text="Text to display after the hunt is over. If you want to include a url (e.g. a google form) at the end use text inside of double curly brackets {{ }} to show where the form will go. "
                  "The text inside the brackets is what will be shown to the user. "
                  "e.g. {{this form}}, users will only see 'this form' but can click it to get to the form specified above",
        max_length=250,
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(start__lt=models.F("end")),
                name="start_before_end",
            ),
            # starting location cannot be the same as ending
            models.CheckConstraint(
                check=~models.Q(starting_location=models.F("ending_location")),
                name="start_not_equal_end",
            ),
            # make sure ending_text contains {{ }} for the form
            models.CheckConstraint(
                check=models.Q(ending_text__contains="{{") & models.Q(
                    ending_text__contains="}}"
                ),
                name="form_in_ending_text",
            ),
            # Ensure there isn't a different hunt running in that timespan
            models.CheckConstraint(
                check=models.Q(start__gt=models.F("end")),
                name="no_overlapping_hunts", # todo check if this works
            ),
        ]


class LogicPuzzleHint(models.Model):
    id = models.AutoField(primary_key=True)
    hint = models.TextField(
        max_length=1024,
        help_text="Hint for the logic puzzle",
    )
    notes = models.TextField(help_text="Internal notes", blank=True)
    qr_index = models.IntegerField(
        help_text="The index of the QR code that this hint is for, that is everyone on their nth QR code will get same same hint (starting from 1)",
        unique=True,
    )

    belongs_to = models.ForeignKey(
        Hunt, related_name="logic_puzzle", on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.hint)

    @classmethod
    def get_clues(cls, team: Team):
        return [
            hint.hint
            for hint in list(LogicPuzzleHint.objects.filter(qr_index__lte=team.qr_len))
        ]

    @classmethod
    def get_clue(cls, team: Team) -> str | None:
        try:
            hint = cls.objects.get(qr_index=team.qr_len)
            return hint.hint
        except cls.DoesNotExist:
            return None
