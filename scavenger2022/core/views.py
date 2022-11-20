from authlib.integrations.base_client.errors import OAuthError
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect, render
from authlib.integrations.django_client import OAuth

oauth = OAuth()
oauth.register('metropolis')


def index(q):
    if (user := q.session.get('user')):
        print(user)
    return render(q, 'core/index.html', {})


def login(q):
    redirect_uri = q.build_absolute_uri(reverse('auth'))
    print(oauth.metropolis.authorize_redirect(q, redirect_uri))
    return oauth.metropolis.authorize_redirect(q, redirect_uri)


def auth(q):
    print(oauth.metropolis)
    print(oauth.metropolis.__dict__)
    try:
        token = oauth.metropolis.authorize_access_token(q)
    except OAuthError as e:
        if e.error == 'access_denied':
            return HttpResponse(f'access_denied: {e.description}')
        raise e
    q.session['user'] = token['userinfo']
    return redirect('/')


def logout(q):
    q.session.pop('user', None)
    return redirect('/')
