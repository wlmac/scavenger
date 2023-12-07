from django.conf import settings
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from ..models import User, Hunt


@require_http_methods(["GET"])
def index(q):
    hunt = Hunt.current_hunt() or Hunt.next_hunt()
    context = dict(first=False)
    context["hunt_name"] = hunt or "The hunt"
    return render(
        q,
        "core/index.html" if q.user.is_authenticated else "core/gate.html",
        context,
    )


@require_http_methods(["GET"])
def credits(q):
    try:
        hintsetters = User.objects.filter(
            groups__in=[
                Group.objects.get(name=settings.LOCATION_SETTERS_NAME),
            ]
        ).all()
        logicsetters = User.objects.filter(
            groups__in=[
                Group.objects.get(name=settings.LOGIC_PUZZLE_SETTERS_NAME),
            ]
        ).all()
    except Group.DoesNotExist:
        hintsetters = []
        logicsetters = []
    return render(
        q, "core/credits.html", dict(hintsetters=hintsetters, logicsetters=logicsetters)
    )
