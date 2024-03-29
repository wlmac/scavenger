from __future__ import annotations

from functools import wraps
from queue import LifoQueue

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import signals
from django.dispatch import Signal, receiver
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from ..models import QrCode, LogicPuzzleHint, Team, Hunt


# NOTE: some of these GET routes are not idempotent, but that should be fine


def team_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        request = args[0]
        if request.user.current_team is None:
            messages.error(
                request,
                _("Please join or create a team before getting a hint."),
            )
            return redirect(reverse("index"))
        return f(*args, **kwargs)

    return wrapped


def upcoming_hunt_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        request = args[0]
        if Hunt.current_hunt() is None and Hunt.next_hunt() is None:
            messages.warning(request, _("No future hunts are scheduled."))
            return redirect(reverse("index"))
        return f(
            *args, **kwargs
        )  # todo: maybe return the hunt object to be used in the view? (more efficient)

    return wrapped


def block_if_current_hunt(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        request = args[0]
        hunt_ = Hunt.current_hunt()
        if (
            request.user.is_impersonate or request.user.is_superuser
        ):  # if the user is an admin or is being impersonated (by a SU), allow them to create a team
            return f(*args, **kwargs)
        if hunt_ is not None and not hunt_.allow_creation_post_start:
            messages.error(
                request,
                _(
                    "Since the hunt has already begun, creating/switching/joining teams is disallowed. "
                    "If you need to do one of the above, please contact an organizer."
                ),
            )
            return redirect(reverse("index"))
        return f(*args, **kwargs)

    return wrapped


def during_hunt(f):
    """
    Decorator for views that checks that the hunt is currently active.

    User can access the view if they meet ANY of the following conditions:
    - The hunt has started and hasn't ended
    - They are on the testers list for that hunt
    - They are a superuser
    """

    @wraps(f)
    @upcoming_hunt_required
    def wrapped(*args, **kwargs):
        hunt_ = Hunt.current_hunt() or Hunt.next_hunt()
        request = args[0]
        if hunt_ is None:
            messages.error(
                request,
                _("No hunt is currently active."),
            )
            return redirect(reverse("index"))

        if any(
            [
                hunt_.started and not hunt_.ended,
                hunt_.testers.contains(request.user),
                request.user.is_superuser,
            ]
        ):
            return f(*args, **kwargs)

        # if they DON'T have perms and the hunt hasn't started
        if hunt_.ended:
            messages.error(
                request,
                _("Contest has ended."),
            )
        else:
            messages.error(
                request,
                _("Contest has not started yet."),
            )
        return redirect(reverse("index"))

    return wrapped


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@during_hunt
def qr(request, key):
    context = dict(first=False)
    codes = QrCode.code_pks(request.user.current_team)
    qr_code: QrCode | None = QrCode.objects.filter(key=key).first()
    if request.user.can_debug:
        return redirect(qr_code.get_admin_url())
    context["qr_code"]: QrCode
    current_i = min(request.user.current_team.current_qr_i, len(codes) - 1)
    if qr_code is None:
        # User just tried brute-forcing keys... lol
        context["offpath"] = True
        return render(request, "core/qr.html", context=context)
    elif (
        qr_code.id == codes[current_i - 1] and len(codes) > 1
    ):  # the user reloaded the page after advancing...or there is only one qr code in the hunt
        return redirect(reverse("qr_current"))
    elif (
        qr_code.id != codes[current_i]
    ):  # fix index out of range (should have been the above anyhow)
        """
        Either the user skipped ahead (is on path) or they found a random qr code (not on path)
        Either way... not allowed
        """
        context["offpath"] = True
        return render(request, "core/qr.html", context=context)
    context["qr"] = qr_code
    context["on_qr"] = True
    i = codes.index(qr_code.id)
    context["nexthint"] = (
        None if len(codes) <= (j := i + 1) else QrCode.objects.get(id=codes[j])
    )
    context["logic_hint"] = LogicPuzzleHint.get_clue(request.user.current_team)
    request.user.current_team.update_current_qr_i(i + 1)
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@during_hunt
def qr_first(request):
    context = dict(first=True)
    # check if the user is on the first qr code
    if request.user.current_team.current_qr_i != 0:
        messages.info(request, _("You are not on the first QR code."))
        return redirect(reverse("qr_current"))
    codes = QrCode.codes(request.user.current_team)
    context["nexthint"] = codes[0]
    # context["logic_hint"] = LogicPuzzleHint.get_clue(request.user.current_team)
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@during_hunt
def qr_current(request):
    i = request.user.current_team.current_qr_i
    if i == 0:  # on first qr code
        return redirect(reverse("qr_first"))
    i -= 1  # we want the index that they are AT not the next one
    context = dict(current=True, on_qr=False)
    codes = QrCode.codes(request.user.current_team)
    context["qr"] = codes[i]
    context["nexthint"] = None if len(codes) <= (j := i + 1) else codes[j]
    context["logic_hint"] = LogicPuzzleHint.get_clue(request.user.current_team)
    return render(request, "core/qr.html", context=context)


global_notifs = Signal()


@receiver(signals.post_save, sender=Team)
def team_change(sender, **kwargs):
    """
    used to reload other people in a team's page when anyone in the team finds a qr code
    """
    global_notifs.send("team_change", orig_sender=sender, kwargs=kwargs)


class SignalStream:
    def __init__(self, signal, pk: int):
        self.signal = signal
        self.pk = pk
        self.q = LifoQueue()
        self.end = False
        self.__setup()

    def __setup(self):
        self.signal.connect(self.__receive)
        self.q.put(("init", {}))

    def __del__(self):
        self.signal.disconnect(self.__receive)

    def __receive(self, sender, **kwargs):
        self.q.put((sender, kwargs))

    def __iter__(self):
        return self

    def __next__(self):
        while 1:
            if self.end:
                raise StopIteration
            sender, kwargs = self.q.get()
            if sender == "team_change":
                team = kwargs["kwargs"]["instance"]
                if self.pk == team.id:
                    self.end = True
                    return f"event: {sender}\ndata: null\n"
                else:
                    continue
            else:
                return f"event: {sender}\ndata: null\n"


@login_required
@require_http_methods(["GET"])
@team_required
@during_hunt
def qr_signal(request):
    s = StreamingHttpResponse(
        SignalStream(signal=global_notifs, pk=request.user.current_team.id),
        content_type="text/event-stream",
    )
    s["Cache-Control"] = "no-cache"
    return s
