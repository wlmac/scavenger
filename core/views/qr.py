import datetime
from functools import wraps
from queue import LifoQueue

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import signals
from django.dispatch import Signal, receiver
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from ..models import QrCode, LogicPuzzleHint, Team, Hunt


# NOTE: some of these GET routes are not idempotent, but that should be fine


def team_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        request = args[0]
        if request.user.team is None:
            messages.error(
                request,
                _("Please join a team or choose to go solo before getting a hint."),
            )
            return redirect(reverse("index"))
        return f(*args, **kwargs)

    return wrapped

def upcoming_hunt_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        request = args[0]
        if Hunt.current_hunt() is None and Hunt.next_hunt() is None:
            messages.error(
                request,
                _("No hunts are in the database, please contact an admin.")
            )
            return redirect(reverse("index"))
        return f(*args, **kwargs) # todo: maybe return the hunt object to be used in the view? (more efficient)

    return wrapped

def during_hunt(f):
    """
    Decorator for views that checks that the hunt is currently active.

    User can access the view if they meet ANY of the following conditions:
    - They have the view_before_start permission and the hunt hasn't ended
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
                request.user.has_perm("core.view_before_start") and not hunt_.ended,
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
    context["qr"] = qr = get_object_or_404(QrCode, key=key)
    context["qr"]: QrCode
    context["hunt"]: Hunt = qr.hunt
    codes = QrCode.code_pks(request.user.team)
    if qr.id not in codes:
        context["offpath"] = True
        return render(request, "core/qr.html", context=context)
    i = codes.index(qr.id)
    context["nextqr"] = (
        None if len(codes) <= (j := i + 1) else QrCode.objects.get(id=codes[j])
    )
    context["logic_hint"] = LogicPuzzleHint.get_clue(request.user.team)
    # TODO: check if they skipped?
    request.user.team.update_current_qr_i(i)
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@during_hunt
def qr_first(request):
    context = dict(first=True)
    # check if the user is on the first qr code
    # if request.user.team.current_qr_i != 0:
    #    messages.error(request, _("You are not on the first QR code."))
    #    return redirect(reverse("qr_current"))
    context["qr"] = QrCode.codes(request.user.team)[0]
    codes = QrCode.code_pks(request.user.team)
    context["nextqr"] = QrCode.objects.get(id=codes[0])
    context["logic_hint"] = LogicPuzzleHint.get_clue(request.user.team)
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@during_hunt
def qr_current(request):
    i = request.user.team.current_qr_i
    context = dict(first=i == 0, current=True)
    context["qr"] = QrCode.codes(request.user.team)[request.user.team.current_qr_i]
    codes = QrCode.code_pks(request.user.team)
    context["nextqr"] = (
        None if len(codes) <= (j := i + 1) else QrCode.objects.get(id=codes[j])
    )
    context["logic_hint"] = LogicPuzzleHint.get_clue(request.user.team)
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@during_hunt
def qr_catalog(request):
    i = request.user.team.current_qr_i
    context = dict(first=i == 0, current=True)
    context["qr"] = QrCode.codes(request.user.team)[: request.user.team.current_qr_i]
    return render(request, "core/qr_catalog.html", context=context)


global_notifs = Signal()


@receiver(signals.post_save, sender=Team)
def team_change(sender, **kwargs):
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
        SignalStream(signal=global_notifs, pk=request.user.team.id),
        content_type="text/event-stream",
    )
    s["Cache-Control"] = "no-cache"
    return s
