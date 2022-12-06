from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.translation import gettext as _


def team_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        request = args[0]
        if not request.user.chosen:
            messages.error(
                request,
                _("Please join a team or choose to go solo before getting a hint."),
            )
            return redirect(reverse("index"))
        return f(*args, **kwargs)

    return wrapped


@login_required
@require_http_methods(("GET", "POST"))
@team_required
def qr(request, key):
    context = dict(first=False)
    context["qr"] = qr = get_object_or_404(QrCode, key=key)
    i = (codes := QrCode.code_pks(request.user)).index(qr.id) + 1
    context["nextqr"] = None if len(codes) <= i else QrCode.objects.get(id=codes[i])
    return render(request, "core/qr.html", context=context)


@login_required
@require_http_methods(("GET", "POST"))
@team_required
def qr_first(request):
    context = dict(first=True)
    context["qr"] = qr = QrCode.codes(request.user)[0]
    i = (codes := QrCode.code_pks(request.user)).index(qr.id) + 1
    context["nextqr"] = None if len(codes) <= i else QrCode.objects.get(id=codes[i])
    return render(request, "core/qr.html", context=context)
