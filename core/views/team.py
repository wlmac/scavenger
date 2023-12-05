from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .qr import team_required, upcoming_hunt_required
from ..forms import TeamJoinForm, TeamMakeForm
from ..models import Team, Invite, generate_invite_code, Hunt


@login_required
@require_http_methods(["GET", "POST"])
@upcoming_hunt_required
def join(request):
    hunt_ = Hunt.current_hunt()
    if hunt_.started and request.user.current_team is not None:
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
            invite_code = Invite.objects.get(code=form.cleaned_data["code"])
            if invite_code is None:
                return HttpResponseBadRequest(
                    "Invalid invite code" + form.cleaned_data["code"]
                )
            team = Team.objects.get(id=invite_code.team_id)
            if team is None:
                return HttpResponseBadRequest(
                    "Invalid team invite code" + form.cleaned_data["code"]
                )
            if not team.is_full():
                team.join(request.user)
                invite_code.invites += 1
                invite_code.save()
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
    hunt_: Hunt = Hunt.current_hunt()
    if not hunt_.allow_creation_post_start:
        messages.error(
            request,
            _(
                "Since the hunt has already begun, making new teams is disallowed. Please contact an admin if you need to make a new team."
            ),
        )
        return redirect(reverse("index"))
    if request.method == "POST":
        form = TeamMakeForm(request.POST)
        if form.is_valid():
            raw: Team = form.save(commit=False)
            raw.hunt = Hunt.current_hunt() or Hunt.next_hunt()
            raw.members.add(request.user)
            raw.save()
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
    Team.objects.create(
        solo=True, hunt=hunt_, name=f"{q.user.username}'s Solo Team", members=[q.user]
    )
    return redirect(reverse("index"))


@login_required
@require_http_methods(["GET"])
@team_required
@upcoming_hunt_required  # redundant
def invite(q):
    invites = Invite.objects.filter(team=q.user.current_team).values_list("code", flat=True)
    if invites.count() == 0:
        print("No invites found, creating one")
        Invite.objects.create(team=q.user.current_team, code=generate_invite_code(), invites=0)
        return invite(q)
    return render(q, "core/team_invite.html", context=dict(invites=invites))
