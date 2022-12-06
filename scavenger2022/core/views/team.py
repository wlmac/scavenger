from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _

from ..models import Team, Invite
from ..forms import TeamJoinForm, TeamMakeForm


@login_required
@require_http_methods(
    (
        "GET",
        "POST",
    )
)
def join(request):
    # TODO: check if aafter cutoff
    if request.method == "POST":
        form = TeamJoinForm(request.POST)
        if form.is_valid():
            invite = Invite.objects.filter(code=form.cleaned_data["code"]).first()
            if invite is None:
                return HttpResponseBadRequest(
                    "Invalid invite code" + form.cleaned_data["code"]
                )
            team = Team.objects.filter(id=invite.team_id).first()
            if not team.is_full():
                team.join(request.user)
                invite.invites += 1
                invite.save()
                messages.success(
                    request, _("Joined team %(team_name)s") % dict(team_name=team.name)
                )
                return redirect("/")
            else:
                messages.error(
                    request,
                    _("Team %(team_name)s is full.") % dict(team_name=team.name),
                )
                return redirect(reverse("join"))
    else:
        if "code" in request.GET:
            form = TeamJoinForm(request.GET)
        else:
            form = TeamJoinForm()
    return render(request, "core/team_join.html", dict(form=form))


@login_required
@require_http_methods(("GET", "POST"))
def make(request):
    if request.method == "POST":
        form = TeamMakeForm(request.POST)
        if form.is_valid():
            form.save()
            request.user.chosen = True
            request.user.team = form.instance
            request.user.save()
            messages.success(
                request,
                _("Made team %(team_name)s")
                % dict(team_name=form.cleaned_data["name"]),
            )
            return redirect(reverse("index"))
    else:
        form = TeamMakeForm()
    return render(request, "core/team_new.html", dict(form=form))


@login_required
@require_http_methods(("POST",))
def solo(q):
    q.user.chosen = True
    q.user.team = Team(solo=True)
    q.user.save()
    return redirect(reverse("index"))
