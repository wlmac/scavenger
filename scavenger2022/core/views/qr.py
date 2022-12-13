import datetime
from queue import LifoQueue

from django.conf import settings
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from ..models import QrCode, LogicPuzzleHint, Team
from django.db.models import signals
from django.dispatch import Signal, receiver
from django.http import StreamingHttpResponse


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


def after_start(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        request = args[0]
        if (
            not request.user.has_perm("core.view_before_start")
            and settings.START > datetime.datetime.now()
        ):
            messages.error(
                request,
                _("Contest has not started yet."),
            )
            return redirect(reverse("index"))
        return f(*args, **kwargs)

    return wrapped


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@after_start
def qr(request, key):
    context = dict(first=False)
    context["qr"] = qr = get_object_or_404(QrCode, key=key)
    i = (codes := QrCode.code_pks(request.user.team)).index(qr.id) + 1
    context["nextqr"] = None if len(codes) <= i else QrCode.objects.get(id=codes[i])
    context["logic_hint"] = LogicPuzzleHint.get_hint(
        request.user.team
    )  # todo maybe this should be under the next two lines?
    # TODO: check if they skipped?
    request.user.team.update_current_qr_i(i - 1)
    request.user.team.save()
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@after_start
def qr_first(request):
    context = dict(first=True)
    context["qr"] = QrCode.codes(request.user.team)[0]
    codes = QrCode.code_pks(request.user.team)
    context["nextqr"] = QrCode.objects.get(id=codes[0])
    request.user.team.update_current_qr_i(0)
    request.user.team.save()
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@after_start
def qr_current(request):
    i = request.user.team.current_qr_i
    context = dict(first=i == 0, current=True)
    context["qr"] = QrCode.codes(request.user.team)[request.user.team.current_qr_i]
    codes = QrCode.code_pks(request.user.team)
    context["nextqr"] = None if len(codes) <= i else QrCode.objects.get(id=codes[i])
    context["logic_hint"] = LogicPuzzleHint.get_hint(request.user.team)
    return render(request, "core/qr.html", context=context)


global_notifs = Signal()


@receiver(signals.post_save, sender=Team)
def team_change(sender, **kwargs):
    # TODO: handle team change? (note: should be as simple as user.team = new_team, ping @jason if u think it's not)
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
@after_start
def qr_signal(request):
    s = StreamingHttpResponse(
        SignalStream(signal=global_notifs, pk=request.user.team.id),
        content_type="text/event-stream",
    )
    s["Cache-Control"] = "no-cache"
    return s
