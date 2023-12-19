from django.urls import path

from .views import auth, index, qr, team, puzzle

urlpatterns = [
    path("", index.index, name="index"),
    path("login/", auth.oauth_login, name="oauth_login"),
    path("auth/", auth.oauth_auth, name="oauth_auth"),
    path("logout/", auth.account_logout, name="account_logout"),
    path("qr/<str:key>", qr.qr, name="qr"),
    path("first", qr.qr_first, name="qr_first"),
    path("current", qr.qr_current, name="qr_current"),
    path("signal", qr.qr_signal, name="qr_signal"),
    path("team", team.team, name="team"),
    path("team/join/", team.join, name="join"),
    path("team/create/", team.create, name="team_create"),
    path("team/invite", team.invite, name="team_invite"),
    path("team/leave", team.leave, name="team_leave"),
    path("clues", puzzle.logic_clues, name="logic_clues"),
    path("credits", index.credits, name="credits"),
]
