from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .qr import team_required, upcoming_hunt_required, block_if_current_hunt
from ..forms import TeamJoinForm, TeamMakeForm
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
@block_if_current_hunt
@upcoming_hunt_required
def make(request):
    if request.method == "POST":
        form = TeamMakeForm(request.POST)
        if form.is_valid():
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
                _("Made team %(team_name)s")
                % dict(team_name=form.cleaned_data["name"]),
            )
            return redirect(reverse("index"))
    else:
        form = TeamMakeForm()
    return render(request, "core/team_new.html", dict(form=form))


@login_required
@upcoming_hunt_required
@block_if_current_hunt
def solo(q: HttpRequest):
    hunt_ = Hunt.current_hunt() or Hunt.next_hunt()
    team_ = Team.objects.create(
        solo=True, hunt=hunt_, name=f"{q.user.username}'s Solo Team"
    )
    team_.join(q.user)
    
    return redirect(reverse("index"))


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
