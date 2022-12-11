from django.urls import path, include
from .views import auth, index, qr, team

urlpatterns = [
    path("", index.index, name="index"),
    path("api/", include("core.api.urls")),
    path("login/", auth.oauth_login, name="oauth_login"),
    path("auth/", auth.oauth_auth, name="oauth_auth"),
    path("logout/", auth.account_logout, name="account_logout"),
    path("qr/<str:key>", qr.qr, name="qr"),
    path("first", qr.qr_first, name="qr_first"),
    path("current", qr.qr_current, name="qr_current"),
    path("team/join/", team.join, name="join"),
    path("team/new", team.make, name="team_new"),
    path("team/solo", team.solo, name="team_solo"),
]
