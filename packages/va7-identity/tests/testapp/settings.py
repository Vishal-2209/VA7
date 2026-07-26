"""Test settings for va7-identity tests."""

from django.conf import settings

settings.configure(
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "django.contrib.sessions",
        "django.contrib.messages",
        "rest_framework",
        "rest_framework_simplejwt",
        "rest_framework_simplejwt.token_blacklist",
        "va7.core",
        "va7.identity",
        "testapp",
    ],
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    },
    MIDDLEWARE=[],
    ROOT_URLCONF="testapp.urls",
    AUTH_USER_MODEL="testapp.User",
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ],
    },
    SIMPLE_JWT={
        "ACCESS_TOKEN_LIFETIME_MINUTES": 15,
        "REFRESH_TOKEN_LIFETIME_DAYS": 14,
    },
    SECRET_KEY="test-secret-key",
    VA7={
        "IDENTITY": {
            "ROLES": {
                "ADMIN": {"label": "Admin", "is_admin": True},
                "MEMBER": {"label": "Member", "is_admin": False},
            },
            "REGISTRATION": {
                "ENABLED": True,
                "REQUIRE_EMAIL_VERIFICATION": True,
            },
        },
    },
)
