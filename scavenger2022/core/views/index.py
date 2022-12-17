from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import Group
from django.views.decorators.http import require_http_methods

from ..models import User


@require_http_methods(["GET"])
def index(q):
    return render(
        q, "core/index.html" if q.user.is_authenticated else "core/gate.html", {}
    )


@require_http_methods(["GET"])
def credits(q):
    try:
        g = Group.objects.get(id=settings.HINTS_GROUP_PK)
        hintsetters = ""
        for user in User.objects.filter(groups__in=[g]):
            hintsetters += f'<a href="https://maclyonsden.com/user/{user.get_full_name()}">{user.username}</a>, '
    except Group.DoesNotExist:
        hintsetters = ""
    return render(q, "core/credits.html", dict(hintsetters=hintsetters.rstrip(", ")))
