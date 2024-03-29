from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .qr import team_required, upcoming_hunt_required, block_if_current_hunt
from ..forms import TeamJoinForm, TeamCreateForm
from ..models import Team, Invite, generate_invite_code, Hunt


@login_required
@require_http_methods(["GET", "POST"])
@block_if_current_hunt
def join(request):
    if request.method == "POST":
        form = TeamJoinForm(request.POST)
        if form.is_valid():
            invite_code = Invite.objects.filter(code=form.cleaned_data["code"]).first()
            if invite_code is None:
                return HttpResponseBadRequest(
                    "Invalid invite code" + form.cleaned_data["code"]
                )
            team = Team.objects.filter(id=invite_code.team_id).first()
            if team is None:
                return HttpResponseBadRequest(
                    "Invalid team invite code" + form.cleaned_data["code"]
                )
            elif team.members.filter(id=request.user.id).exists():
                messages.error(
                    request,
                    _("You are already in team %(team_name)s")
                    % dict(team_name=team.name),
                )
                return redirect(reverse("team"))
            elif not team.is_full:
                team.join(request.user)
                invite_code.invites += 1
                invite_code.save()
                messages.success(
                    request,
                    _("Joined team %(team_name)s") % dict(team_name=team.name),
                )
                return redirect(reverse("index"))  # change to team?
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
@block_if_current_hunt
@upcoming_hunt_required
def create(request):
    if request.method == "POST":
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            if request.user.in_team:
                messages.error(
                    request,
                    _(
                        "You are already in a team. Leave your current team to create a new one."
                    ),
                )
                return redirect(reverse("team_leave"))
            raw: Team = form.save(commit=False)
            raw.hunt = Hunt.current_hunt() or Hunt.next_hunt()
            raw: Team = form.save()

            if request.user.in_team:
                team = Team.objects.get(id=request.user.current_team.id)
                team.leave(request.user)
            raw.join(request.user)
            Invite.objects.get_or_create(
                team=raw, code=generate_invite_code(), invites=0
            )
            messages.success(
                request,
                _("Created team %(team_name)s")
                % dict(team_name=form.cleaned_data["name"]),
            )
            return redirect(reverse("index"))
    else:
        form = TeamCreateForm()
    return render(request, "core/team_create.html", dict(form=form))


@login_required
@require_http_methods(["POST", "GET"])
@team_required
@block_if_current_hunt
def leave(request):
    if request.method == "POST":
        team = Team.objects.get(id=request.user.current_team.id)
        team.leave(request.user)
        messages.success(
            request, _("Left team %(team_name)s") % dict(team_name=team.name)
        )
        return redirect(reverse("index"))
    return render(request, "core/team_leave.html")


@login_required
@require_http_methods(["GET"])
@team_required
def team(q: HttpRequest):
    return render(q, "core/team.html")


@login_required
@require_http_methods(["GET"])
@team_required
@block_if_current_hunt  # redundant
def invite(q):
    invites = Invite.objects.filter(team=q.user.current_team).values_list(
        "code", flat=True
    )
    if invites.count() == 0:
        print("No invites found, creating one")
        Invite.objects.create(
            team=q.user.current_team, code=generate_invite_code(), invites=0
        )
        return invite(q)
    return render(q, "core/team_invite.html", context=dict(invites=invites))
