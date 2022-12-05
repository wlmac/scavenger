from django.urls import path, include
from .views import auth, index, qr, team

urlpatterns = [
    path("", index.index, name="index"),
    path("api/", include("core.api.urls")),
    path("login/", auth.oauth_login, name="oauth_login"),
    path("auth/", auth.oauth_auth, name="oauth_auth"),
    path("logout/", auth.account_logout, name="account_logout"),
    path("qr/<int:pk>", qr.QrView.as_view(), name="qr"),
    path("team/join/", team.join, name="join"),
    path("team/new", team.make, name="team_new"),
    path("team/solo", team.solo, name="team_solo"),
]
