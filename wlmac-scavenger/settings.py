import os

from pathlib import Path
from typing import Final, List

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS: List[str] = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "fontawesomefree",
    "core",
    "impersonate",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
]

ROOT_URLCONF = "wlmac-scavenger.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.start",
            ],
        },
    },
]

WSGI_APPLICATION = "wlmac-scavenger.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGIN_URL = "/login"

LOGIN_REDIRECT_URL = "/"

AUTH_USER_MODEL = "core.User"

LANGUAGE_CODE = "en"

TIME_ZONE = "America/Toronto"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = (("static", BASE_DIR / "core/static/core"),)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

base_url = "https://maclyonsden.com"
YASOI = dict(
    client_id="",  # unset
    client_secret="",  # unset
    authorize_url=f"{base_url}/authorize",
    token_url=f"{base_url}/token/",
    me_url=f"{base_url}/api/me/internal",
    scope="me_meta internal",
)

HINTS_GROUP_PK: Final[int] = 1  # the pk of the hints group (defined in commands/init.py)

try:
    with open(os.path.join(os.path.dirname(__file__), "local_settings.py")) as f:
        exec(f.read(), globals())
except IOError:
    raise TypeError("local_settings.py not found")

SECRET_KEY  # type: ignore
START  # type: ignore
END  # type: ignore
