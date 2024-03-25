"""
Django settings for livepublication_portal project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from globus_sdk.scopes import GCSCollectionScopeBuilder, TransferScopes
import globus_sdk
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-generate-new-key-with-openssl-rand-hex-32-asdf-aoeu"

PROJECT_TITLE = "LivePublication"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Used to simplify making a pretty Django form
    "crispy_forms",
    "crispy_bootstrap4",
    # Used for providing Globus Auth helpers and some starter templates
    "globus_portal_framework",
    "social_django",
    # This app
    "livepublication_portal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "globus_portal_framework.middleware.ExpiredTokenMiddleware",
    "globus_portal_framework.middleware.GlobusAuthExceptionMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

# Authentication backends setup OAuth2 handling and where user data should be
# stored
AUTHENTICATION_BACKENDS = [
    "globus_portal_framework.auth.GlobusOpenIdConnect",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "livepublication_portal.urls"


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates", BASE_DIR / "livepublication_portal"/ "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "globus_portal_framework.context_processors.globals",
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "sqlite",
    }
}

# This is a general Django setting if views need to redirect to login
# https://docs.djangoproject.com/en/4.2/ref/settings/#login-url
LOGIN_URL = "/login/globus"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# SCOPES

# Base scopes
SOCIAL_AUTH_GLOBUS_SCOPE = [
    "openid",
    "profile",
    "email",
]

# Adding the flow UUIDs to the scopes
FLOWS_PATH = BASE_DIR / "livepublication_portal" / "flows"
flows_UUIDs = []

try:
    with open(FLOWS_PATH / "flows.json", 'r') as f:
        for line in f:
            flow = json.loads(line.strip())
            flows_UUIDs.append(flow['uuid'])
except FileNotFoundError:
    print("flows.json file not found.")

# Add scope for each flow UUID
for uuid in flows_UUIDs:
    flow_scope_name = f"flow_{uuid.replace('-', '_')}_user"
    scope_string = globus_sdk.SpecificFlowClient(uuid).scopes.url_scope_string(flow_scope_name)
    SOCIAL_AUTH_GLOBUS_SCOPE.append(scope_string)

# ADD scopes for LivePublication GCS & transfer
SOCIAL_AUTH_GLOBUS_SCOPE.append(TransferScopes.all)

COLLECTION_ID = [
    "b782400e-3e59-412c-8f73-56cd0782301f",
    "d920d765-dda0-41cb-a30e-11f5a5f455a4"
]
for collection in COLLECTION_ID:
    scope_buildier = GCSCollectionScopeBuilder(collection)
    scope_string = scope_buildier.url_scope_string("data_access")
    SOCIAL_AUTH_GLOBUS_SCOPE.append(scope_string)

# Add scope for Globus Compute node (Note this works becuase the confidential client
# which manages this server, also owns the compute node)
# URL from https://globus-compute.readthedocs.io/en/latest/sdk.html#client-credentials-with-globus-compute-clients
GLOBUS_COMPUTE_SCOPE = "https://auth.globus.org/scopes/facd7ccc-c5f4-42aa-916b-a0e270e2c2a9/all"
SOCIAL_AUTH_GLOBUS_SCOPE.append(GLOBUS_COMPUTE_SCOPE)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "stream": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["stream"], "level": "INFO"},
        "django.db.backends": {"handlers": ["stream"], "level": "WARNING"},
        "globus_portal_framework": {"handlers": ["stream"], "level": "DEBUG"},
        "livepublication_portal": {
            "handlers": ["stream"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"

try:
    from livepublication_portal.local_settings import *
except ImportError:
    contents = """
        SOCIAL_AUTH_GLOBUS_KEY = "key"
        SOCIAL_AUTH_GLOBUS_SECRET = "secret"
    """
    print(
        f'Create a file called "local_settings.py" next to your "settings.py" file with the following:\n\n {contents}'
    )
    raise Exception("Portal Start Failed, please resolve the auth errors first!")