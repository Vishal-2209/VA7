"""Tests for identity views."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestRegisterView:

    def test_register_success(self, api_client):
        response = api_client.post("/identity/register/", {
            "email": "new@example.com",
            "password": "newpass123",
        }, format="json")
        assert response.status_code == 201
        assert "tokens" in response.data
        assert "user" in response.data
        assert response.data["email_verification_required"] is True

    def test_register_duplicate_email(self, api_client, user):
        response = api_client.post("/identity/register/", {
            "email": "test@example.com",
            "password": "pass123",
        }, format="json")
        assert response.status_code == 400

    def test_register_short_password(self, api_client):
        response = api_client.post("/identity/register/", {
            "email": "short@example.com",
            "password": "123",
        }, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginView:

    def test_login_success(self, api_client, user):
        response = api_client.post("/identity/login/", {
            "email": "test@example.com",
            "password": "testpass123",
        }, format="json")
        assert response.status_code == 200
        assert "tokens" in response.data
        assert "user" in response.data

    def test_login_wrong_password(self, api_client, user):
        response = api_client.post("/identity/login/", {
            "email": "test@example.com",
            "password": "wrongpass",
        }, format="json")
        assert response.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        response = api_client.post("/identity/login/", {
            "email": "nobody@example.com",
            "password": "pass123",
        }, format="json")
        assert response.status_code == 401


@pytest.mark.django_db
class TestProfileView:

    def test_get_profile(self, api_client, user):
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = api_client.get("/identity/profile/")
        assert response.status_code == 200
        assert response.data["email"] == "test@example.com"

    def test_update_profile(self, api_client, user):
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = api_client.patch(
            "/identity/profile/",
            {"first_name": "Updated"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["first_name"] == "Updated"

    def test_unauthenticated(self, api_client):
        response = api_client.get("/identity/profile/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestLogoutView:

    def test_logout_success(self, api_client, user):
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        response = api_client.post(
            "/identity/logout/",
            {"refresh": str(refresh)},
            format="json",
        )
        assert response.status_code == 204

    def test_logout_unauthenticated(self, api_client):
        response = api_client.post("/identity/logout/", {}, format="json")
        assert response.status_code == 401


@pytest.mark.django_db
class TestPasswordResetView:

    def test_request_reset(self, api_client, user):
        response = api_client.post(
            "/identity/password-reset/request/",
            {"email": user.email},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["otp_sent"] is True

    def test_confirm_reset(self, api_client, user):
        api_client.post(
            "/identity/password-reset/request/",
            {"email": user.email},
            format="json",
        )
        from va7.identity.services.otp import OTPService
        otp = OTPService().generate(f"password_reset:{user.pk}")

        response = api_client.post(
            "/identity/password-reset/confirm/",
            {
                "email": user.email,
                "otp": otp,
                "new_password": "newpass456",
            },
            format="json",
        )
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.check_password("newpass456")


@pytest.mark.django_db
class TestEmailVerificationView:

    def test_verify_email(self, api_client, user):
        api_client.post(
            "/identity/resend-verification/",
            {"email": user.email},
            format="json",
        )
        from va7.identity.services.otp import OTPService
        otp = OTPService().generate(f"email_verify:{user.pk}")

        response = api_client.post(
            "/identity/verify-email/",
            {"email": user.email, "otp": otp},
            format="json",
        )
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.is_email_verified is True

    def test_resend_verification(self, api_client, user):
        response = api_client.post(
            "/identity/resend-verification/",
            {"email": user.email},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["otp_sent"] is True
