import sys
import os

# Make va7 namespace package discoverable
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_core = os.path.abspath(os.path.join(_root, "va7-core"))
_identity = os.path.abspath(os.path.join(_root, "va7-identity"))

for p in [_root, _core, _identity]:
    if p not in sys.path:
        sys.path.insert(0, p)

from django.conf import settings

if not settings.configured:
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

import django
django.setup()

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from va7.identity.services import (
    OTPService,
    RegistrationService,
    PasswordResetService,
    EmailVerificationService,
)


@pytest.fixture
def User():
    return get_user_model()


@pytest.fixture
def user(db, User):
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user(db, User):
    return User.objects.create_user(
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
        role="ADMIN",
        is_staff=True,
    )


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def otp_service():
    return OTPService()


@pytest.fixture
def registration_service():
    return RegistrationService()


@pytest.fixture
def password_reset_service():
    return PasswordResetService()


@pytest.fixture
def email_verification_service():
    return EmailVerificationService()
