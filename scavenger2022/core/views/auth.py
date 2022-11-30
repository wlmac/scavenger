from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from authlib.integrations.django_client import OAuth
import requests

import base64
import hashlib
import secrets

from urllib.parse import urlencode

from ..models import User

oauth = OAuth()
oauth.register("metropolis")


def pkce1(q):
    q.session["yasoi_code_verifier"] = code_verifier = secrets.token_urlsafe(96)
    print('code_verifier', code_verifier)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('ascii')).digest()).decode('ascii')
    # remove 1 or 2 base64 padding
    code_challenge = code_challenge.removesuffix('=')
    code_challenge = code_challenge.removesuffix('=')
    print('code_challenge', code_challenge)
    code_challenge_method = "S256"
    return dict(code_challenge=code_challenge, code_challenge_method=code_challenge_method)


def pkce2(q):
    code_verifier = q.session["yasoi_code_verifier"]
    return dict(code_verifier=code_verifier)


@require_http_methods(("GET",))
def oauth_login(q):
    redirect_uri = q.build_absolute_uri(reverse("oauth_auth"))
    state = secrets.token_urlsafe(32)
    q.session["yasoi_state"] = state
    pkce_params = pkce1(q)
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
                **pkce_params,
            )
        )
    )


def oauth_auth(q):
    redirect_uri = q.build_absolute_uri(reverse("oauth_auth"))
    print("死ねる勇気あるかな", list(q.session.items()))
    given_state = q.GET["state"]
    expected_state = q.session['yasoi_state']
    if expected_state != given_state:
        raise TypeError('state mismatch')
    if 'error' in q.GET:
        raise RuntimeError(f'{q.GET["error"]}: {q.GET["error_description"]}')
    pkce_params = pkce2(q)
    code = q.GET["code"]
    q2 = requests.post(
        settings.YASOI["token_url"],
        data=dict(
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
            **{key: settings.YASOI[key] for key in ("client_id", "client_secret")},
            **pkce_params,
        ),
    )
    print(q2.status_code, q2.text)
    if q2.status_code == 400:
        data = q2.json()
        raise RuntimeError(f"{data['error']}: {data.get('error_description')}")
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
