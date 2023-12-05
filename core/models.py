from __future__ import annotations

import random
import secrets
from typing import List

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Func, F, DurationField, Case, DateTimeField, When
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.utils.html import format_html


def generate_invite_code():
    return secrets.token_hex(4)


class User(AbstractUser):
    metropolis_id = models.IntegerField()
    refresh_token = models.CharField(max_length=128)

    @property
    def current_team(self) -> Team | None:
        """Returns the team that the user is currently on for the current or upcoming hunt.
        If the user is not on a team, return None"""

        current_ = Hunt.current_hunt()
        next_ = Hunt.next_hunt()
        if current_ is None and next_ is None:
            return None
        return self.teams.get(hunt=current_) if current_ else self.teams.get(hunt=next_)

    @property
    def in_team(self) -> bool:
        """Returns True if the user is in a team for the current or upcoming hunt."""
        return self.current_team is not None


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
    def codes(
        cls, team: "Team"
    ) -> List[QrCode]:  # todo: have this return an ordered QuerySet instead of a list
        pks = QrCode.code_pks(team)
        return [QrCode.objects.get(id=a) for a in pks]

    @classmethod
    def code_pks(cls, team: "Team"):
        """
        Returns the QR codes that the team has to find in order.
        The algorithm behind this system is as follows:
        1. Get the hunt that the team belongs to
        2. Get the QR codes that are in the middle of the path for the specified hunt
        3. Shuffle QR codes (using the team id appended to hunt id as the key)
        4. Get the first n QR codes (n being the path length)
        5. Add the starting and ending QR codes to list
        6. Return the list
        """
        hunt: Hunt = team.hunt
        r = random.Random(str(hunt.id) + str(team.id))
        hunt_codes = hunt.middle_locations.all()
        pks = [a["pk"] for a in hunt_codes.values("pk")]
        r.shuffle(pks)
        pks = pks[: hunt.path_length]
        if hunt_end := hunt.ending_location:
            pks.append(hunt_end.id)
        if hunt_start := hunt.starting_location:
            pks.insert(0, hunt_start.id)
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
    # owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="teams_ownership") potentially add this later
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True, null=True)
    is_open = models.BooleanField(
        default=False
    )  # todo use this field to have a club-like page so you can join an open team (future feature)
    current_qr_i = models.IntegerField(default=0)
    solo = models.BooleanField(default=False)
    members = models.ManyToManyField(
        related_name="teams", related_query_name="teams", to=User
    )
    hunt = models.ForeignKey("Hunt", on_delete=models.CASCADE, related_name="teams")

    def update_current_qr_i(self, i: int):
        self.current_qr_i = max(self.current_qr_i, i)
        self.save()

    @property
    def is_full(self):
        return self.members.count() >= self.hunt.max_team_size

    @property
    def is_empty(self):
        return self.members.count() == 0

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
        """Amount of codes the team has completed (+1) (assuming no skips)"""
        return int(self.current_qr_i) + 1

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        data = super().save(*args, **kwargs)
        if self._state.adding:  # only generate key on creation not on update
            Invite.objects.create(team=self, code=generate_invite_code())
        return data


class Invite(models.Model):
    invites = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="invites")
    code = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return str(self.team.name)


class Hunt(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)
    start = models.DateTimeField(blank=False, null=False)
    end = models.DateTimeField(blank=False, null=False)
    max_team_size = models.PositiveSmallIntegerField(
        default=4, help_text="Max Team size"
    )
    path_length = models.PositiveSmallIntegerField(
        default=13,
        help_text="Length of the path: The amount of codes each time will have to find before the end. (not including start/end)",
    )
    starting_location = models.ForeignKey(
        QrCode,
        on_delete=models.PROTECT,
        related_name="starting_location",
        blank=True,
        null=True,
        help_text="(Optional) A specified starting location for the hunt. All teams will have to scan this QR code as their first.",
    )
    ending_location = models.ForeignKey(
        QrCode,
        on_delete=models.PROTECT,
        related_name="ending_location",
        blank=True,
        null=True,
        help_text="(Optional) A specified ending location for the hunt. All teams will get as their last location.",
    )
    middle_locations = models.ManyToManyField(
        QrCode,
        related_name="hunt",
        help_text="Possible locations that are not the start or end",
        blank=False,
    )
    testers = models.ManyToManyField(
        User,
        related_name="testers",
        help_text="Users that can access this hunt before it starts as well as after",
        blank=True,
    )
    form_url = models.URLField(
        help_text="Google form to fill out after the hunt", null=True, blank=True
    )
    ending_text = models.TextField(
        help_text="Text to display after the hunt is over. If you want to include a url (e.g. a google form) at the end use text inside of double curly brackets {{ }} to show where the form will go. "
        "The text inside the brackets is what will be shown to the user. "
        "e.g. {{this form}}, users will only see 'this form' but can click it to get to the form specified above",
        max_length=250,
    )
    allow_creation_post_start = models.BooleanField(
        default=False,
        help_text="Allow users to create teams after the hunt has started",
    )

    def __str__(self):
        return self.name

    @classmethod
    def closest_hunt(cls) -> Hunt | None:
        now = timezone.now()
        closest_hunt = (
            Hunt.objects.annotate(
                selected_time=Case(  # if we should use the start or end time (if it's in the future or past)
                    When(start__lt=now, then=F("end")),
                    default=F("start"),
                    output_field=DateTimeField(),
                )
            )
            .annotate(
                time_difference=Func(
                    F("selected_time") - now,
                    function="ABS",
                    output_field=DurationField(),
                )
            )
            .order_by("time_difference")
        )
        if closest_hunt is None:
            return None
        return closest_hunt.first()

    @classmethod
    def current_hunt(cls) -> Hunt | None:
        try:
            return cls.objects.get(start__lte=timezone.now(), end__gte=timezone.now())
        except cls.DoesNotExist:
            return None

    @classmethod
    def next_hunt(cls) -> Hunt | None:
        try:
            return (
                cls.objects.filter(start__gte=timezone.now()).order_by("start").first()
            )
        except IndexError:
            return None

    @property
    def started(self):
        return self.start < timezone.now()

    @property
    def ended(self):
        return self.end < timezone.now()

    def clean(self):
        """
        Due to how this was designed, it is not possible to have multiple hunts running at the same time.
        This method prevents that from happening.
        """

        overlapping_events = Hunt.objects.filter(
            start__lte=self.start, end__gte=self.end  # todo fix
        ).exclude(pk=self.pk)
        if overlapping_events.exists():
            raise ValidationError(
                "This event overlaps with existing events. Please choose a different time. Or Delete the other event."
            )

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


@receiver(m2m_changed, sender=Team)
def remove_empty_teams(sender, instance: Team, action, **kwargs):
    print(sender, instance, action, kwargs)
    if action == "post_clear":
        try:
            instance.delete()
        except:
            pass
    elif action == "post_remove":
        if instance.is_empty():
            print("Deleting empty team: ", instance.name)
            instance.delete()
