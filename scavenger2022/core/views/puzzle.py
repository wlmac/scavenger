from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .qr import team_required, after_start
from ..models import LogicPuzzleHint


@login_required
@require_http_methods(["GET", "POST"])
@team_required
@after_start
def logic_clues(request):
    context = dict(logic_clues=LogicPuzzleHint.get_clues(request.user.team))
    return render(request, "core/logic_hints.html", context=context)
