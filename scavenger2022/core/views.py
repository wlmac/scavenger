from authlib.integrations.base_client.errors import OAuthError
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from authlib.integrations.django_client import OAuth
import requests

from urllib.parse import urlencode, urljoin

from .models import User

oauth = OAuth()
oauth.register("metropolis")


@require_http_methods(("GET",))
def index(q):
    if user := q.session.get("user"):
        print(user)
    return render(q, "core/index.html", {})


@require_http_methods(("GET",))
def oauth_login(q):
    redirect_uri = q.build_absolute_uri(reverse("oauth_auth"))
    # state = secrets.token_urlsafe(32)
    # TODO: fix state
    # TODO: pkce
    state = "死ねる勇気もないよ"
    q.session["yasoi_state"] = state
    print("死ねる勇気あるかな", list(q.session.items()))
    return redirect(
        settings.YASOI["authorize_url"]
        + "?"
        + urlencode(
            dict(
                response_type="code",
                client_id=settings.YASOI["client_id"],
                redirect_uri=redirect_uri,
                scope="me_meta",
                state=state,
            )
        )
    )


def oauth_auth(q):
    redirect_uri = q.build_absolute_uri(reverse("oauth_auth"))
    print("死ねる勇気あるかな", list(q.session.items()))
    given_state = q.GET["state"]
    # expected_state = q.session['yasoi_state']
    expected_state = "死ねる勇気もないよ"
    if expected_state != given_state:
        raise RuntimeError("ﾀﾋ")
    code = q.GET["code"]
    q2 = requests.post(
        settings.YASOI["token_url"],
        data=dict(
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
            **{key: settings.YASOI[key] for key in ("client_id", "client_secret")},
        ),
    )
    q2.raise_for_status()
    # TODO: handle errors (*˘︶˘*).｡.:*♡
    s2d = q2.json()
    access_token = s2d["access_token"]
    refresh_token = s2d["refresh_token"]
    q3 = requests.get(
        settings.YASOI["me_url"], headers={"Authorization": f"Bearer {access_token}"}
    )
    q3.raise_for_status()
    s3d = q3.json()
    try:
        u = User.objects.get(metropolis_id=s3d["id"])
    except User.DoesNotExist:
        u = User(
            username=s3d["username"],
            first_name=s3d["first_name"],
            last_name=s3d["last_name"],
            metropolis_id=s3d["id"],
        )
    u.refresh_token = refresh_token
    u.save()
    login(q, u)
    messages.success(q, "Logged in.")
    return redirect("/")


@require_http_methods(("POST",))
def account_logout(q):
    logout(q)
    return redirect("/")
