from django.http import HttpResponseBadRequest
from django.shortcuts import redirect

from ..models import Team, Invite


def join(request, code):
    """
    http://127.0.0.1:8001/team/join/12/
    """
    if not request.user.is_authenticated:
        return redirect(f"/?next={request.path}")
    invite = Invite.objects.filter(code=code).first()
    if invite is None:
        return HttpResponseBadRequest("Invalid invite code")
    team = Team.objects.filter(id=invite.team_id).first()
    if not team.is_full():
        team.join(request.user)
        invite.invites += 1
        invite.save()
        return redirect("/")
        # return redirect("team", team.id) # todo once team page is made change it to this.
