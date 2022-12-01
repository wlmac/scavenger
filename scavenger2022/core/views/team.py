from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from ..models import Team, Invite


@login_required
@require_http_methods(("POST",))
def join(request, code):
    """
    http://127.0.0.1:8001/team/join/12/
    """
    invite = Invite.objects.filter(code=code).first()
    if invite is None:
        return HttpResponseBadRequest("Invalid invite code")
    team = Team.objects.filter(id=invite.team_id).first()
    if not team.is_full():
        team.join(request.user)
        invite.invites += 1
        invite.save()
        return redirect("/")
        # return redirect("team", team.id) # TODO: once team page is made change it to this.


@login_required
@require_http_methods(("POST",))
def make(q):
    raise NotImplementedError()


@login_required
@require_http_methods(("POST",))
def solo(q):
    q.user.chosen = True
    q.user.save()
    return redirect(reverse("index"))
