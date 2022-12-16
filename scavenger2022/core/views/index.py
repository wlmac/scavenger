from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def index(q):
    return render(
        q, "core/index.html" if q.user.is_authenticated else "core/gate.html", {}
    )
