from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(("GET",))
def index(q):
    if user := q.session.get("user"):
        print(user)
    return render(q, "core/index.html", {})
