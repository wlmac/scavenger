import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _

from ..models import Team, Invite, generate_invite_code, Hunt
from ..forms import TeamJoinForm, TeamMakeForm
from .qr import team_required, upcoming_hunt_required


@login_required
@require_http_methods(["GET", "POST"])
@upcoming_hunt_required
def join(request):
    hunt_ = Hunt.current_hunt() or Hunt.next_hunt()
    if hunt_.started and request.user.team is not None:
        messages.error(
            request,
            _(
                "Since the hunt has already begun, switching teams is disallowed. "
                "If you need to switch teams, please contact an admin."
            ),
        )
        return redirect(reverse("index"))
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
                    request,
                    _("Joined team %(team_name)s") % dict(team_name=team.name),
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
@require_http_methods(["GET", "POST"])
@upcoming_hunt_required
def make(request):
    hunt_ = Hunt.current_hunt() or Hunt.next_hunt()
    if hunt_.started and request.user.team is not None:
        messages.error(
            request,
            _("Since the hunt has already begun, making new teams is disallowed."),
        )
        return redirect(reverse("index"))
    if request.method == "POST":
        form = TeamMakeForm(request.POST)
        if form.is_valid():
            raw: Team = form.save(commit=False)
            raw.hunt = Hunt.current_hunt() or Hunt.next_hunt()
            raw.save()
            request.user.team = raw
            request.user.save()
            Invite.objects.get_or_create(
                team=raw, code=generate_invite_code(), invites=0
            )
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
@upcoming_hunt_required
def solo(q: HttpRequest):
    hunt_ = Hunt.current_hunt() or Hunt.next_hunt()
    team = Team.objects.create(
        solo=True, hunt=hunt_, name=f"{q.user.username}'s Solo Team"
    )
    q.user.team = team
    q.user.save()
    return redirect(reverse("index"))


@login_required
@require_http_methods(["GET"])
@team_required
@upcoming_hunt_required  # redundant
def invite(q):
    invites = Invite.objects.filter(team=q.user.team).values_list("code", flat=True)
    if invites.count() == 0:
        print("No invites found, creating one")
        Invite.objects.create(team=q.user.team, code=generate_invite_code(), invites=0)
        return invite(q)
    return render(q, "core/team_invite.html", context=dict(invites=invites))
