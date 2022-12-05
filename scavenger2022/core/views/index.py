from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(("GET",))
def index(q):
    return render(q, "core/index.html", {})
