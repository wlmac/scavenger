import random
import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    metropolis_id = models.IntegerField()
    refresh_token = models.CharField(max_length=128)
    team = models.ForeignKey(
        "Team", related_name="members", on_delete=models.CASCADE, blank=True, null=True
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
    key = models.CharField(max_length=64, unique=True, default=generate_hint_key)

    def __str__(self):
        return self.short or str(self.id)

    @classmethod
    def codes(cls, team: "Team"):
        pks = QrCode.code_pks(team)
        return [QrCode.objects.get(id=a) for a in pks]

    @classmethod
    def code_pks(cls, team: "Team"):
        r = random.Random(team.id)
        pks = [a["pk"] for a in QrCode.objects.all().values("pk")]
        r.shuffle(pks)
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
        permissions = [("view_before_cutoff", "Play game before cutoff")]


class Team(models.Model):
    # owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="teams_ownership") potentially add this later
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True, null=True)
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
    solo = models.BooleanField(default=False)

    def next_code(self) -> QrCode:
        qr_codes = list(QrCode.objects.exclude(id__in=self.completed_qr_codes.all()))
        item = random.choice(qr_codes)
        self.current_qr_code = item.id
        return item

    @property
    def members(self):
        """Returns all members of the team, it's  a related manager so to convert to queryset use .all() or filter it."""
        return User.objects.filter(team=str(self.id))

    def is_full(self):
        return self.members.count() >= settings.MAX_TEAM_SIZE

    def join(self, user: User):
        if user in self.members.all():
            return
        if self.is_full():
            raise IndexError("Team is full")
        user.team = self
        user.save()

    def invites(self):
        return Invite.objects.filter(team=self)

    def get_qr_nth(self):
        """Get the total amount of qr codes the team has completed"""
        print(
            int(self.completed_qr_codes.count()) + 1
        )  # todo remove. this is just for debugging
        return int(self.completed_qr_codes.count()) + 1

    def __str__(self):
        return str(self.name)


def generate_invite_code():
    return secrets.token_hex(3)


class Invite(models.Model):
    invites = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    code = models.CharField(max_length=32, unique=True)


# class Hunt(models.Model):
#    id = models.AutoField(primary_key=True)
#    name = models.CharField(max_length=64)
#    start = models.DateTimeField()
#    end = models.DateTimeField()
#    is_active = models.BooleanField(default=False)
#    team_size = models.IntegerField(default=4, help_text="Max Team size")
#    final_qr_id = models.IntegerField(null=True, blank=True)
#
#    def __str__(self):
#        return self.name


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

    # belongs_to = models.ForeignKey(Hunt, related_name="logic_puzzle_hunt", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.hint)

    def get_hint(self, team: Team):
        return self.objects.get(qr_index=team.get_qr_nth()).hint
