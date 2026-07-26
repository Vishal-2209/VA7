"""Tests for identity services."""

import pytest
from django.contrib.auth import get_user_model

from va7.identity.services.otp import OTPService, OTPMethod
from va7.identity.services.registration import RegistrationService
from va7.identity.services.password import PasswordResetService
from va7.identity.services.email import EmailVerificationService
from va7.core.events import emit

User = get_user_model()


@pytest.mark.django_db
class TestOTPMethod:

    def test_generate_and_validate(self):
        method = OTPMethod(length=6, ttl=300)
        otp = method.generate("test_purpose")
        assert len(otp) == 6
        assert otp.isdigit()

        is_valid, reason = method.validate("test_purpose", otp)
        assert is_valid is True
        assert reason == "valid"

    def test_validate_wrong_otp(self):
        method = OTPMethod()
        method.generate("test_purpose")
        is_valid, reason = method.validate("test_purpose", "000000")
        assert is_valid is False
        assert reason == "invalid"

    def test_validate_expired(self):
        from django.core.cache import cache
        method = OTPMethod()
        otp = method.generate("test_purpose")
        cache.delete(method._key("test_purpose"))
        is_valid, reason = method.validate("test_purpose", otp)
        assert is_valid is False
        assert reason == "expired"

    def test_validate_max_attempts(self):
        method = OTPMethod(max_attempts=3)
        otp = method.generate("test_purpose")
        for _ in range(3):
            method.validate("test_purpose", "000000")
        is_valid, reason = method.validate("test_purpose", otp)
        assert is_valid is False
        assert reason == "max_attempts"

    def test_name(self):
        method = OTPMethod()
        assert method.name == "otp"


@pytest.mark.django_db
class TestOTPService:

    def test_generate_and_validate(self, otp_service):
        otp = otp_service.generate("test_purpose")
        assert len(otp) == 6
        assert otp.isdigit()

        is_valid, reason = otp_service.validate("test_purpose", otp)
        assert is_valid is True
        assert reason == "valid"

    def test_can_resend(self, otp_service):
        assert otp_service.can_resend("test_purpose") is True

    def test_increment_resend(self, otp_service):
        otp_service.increment_resend("test_purpose")
        otp_service.increment_resend("test_purpose")
        assert otp_service.can_resend("test_purpose") is True
        otp_service.increment_resend("test_purpose")
        assert otp_service.can_resend("test_purpose") is False


@pytest.mark.django_db
class TestRegistrationService:

    def test_register_user(self, registration_service):
        user, require_verification = registration_service.register(
            email="new@example.com",
            password="newpass123",
        )
        assert user.pk is not None
        assert user.email == "new@example.com"
        assert require_verification is True

    def test_register_user_no_verification(self, db):
        from va7.conf import settings as va7_settings
        original = va7_settings.IDENTITY.get("REGISTRATION", {}).copy()

        va7_settings._config["IDENTITY"]["REGISTRATION"] = {
            "ENABLED": True,
            "REQUIRE_EMAIL_VERIFICATION": False,
        }

        try:
            service = RegistrationService()
            user, require_verification = service.register(
                email="no_verify@example.com",
                password="pass123",
            )
            assert require_verification is False
            user.refresh_from_db()
            assert user.is_email_verified is True
        finally:
            va7_settings._config["IDENTITY"]["REGISTRATION"] = original

    def test_register_emits_event(self, registration_service):
        from va7.core.events import listen

        events = []
        listen("identity.user_registered", lambda sender, **kwargs: events.append(kwargs))

        user, _ = registration_service.register(
            email="event@example.com",
            password="pass123",
        )
        assert len(events) == 1
        assert events[0]["user"] == user


@pytest.mark.django_db
class TestPasswordResetService:

    def test_request_reset(self, password_reset_service, user):
        otp_sent, returned_user = password_reset_service.request_reset(user.email)
        assert otp_sent is True
        assert returned_user == user

    def test_request_reset_nonexistent_email(self, password_reset_service):
        otp_sent, user = password_reset_service.request_reset("nonexistent@example.com")
        assert otp_sent is True
        assert user is None

    def test_confirm_reset_success(self, password_reset_service, user):
        password_reset_service.request_reset(user.email)
        otp = OTPService().generate(f"password_reset:{user.pk}")

        success, reason = password_reset_service.confirm_reset(
            user.email, otp, "newpass456"
        )
        assert success is True

        user.refresh_from_db()
        assert user.check_password("newpass456")

    def test_confirm_reset_wrong_otp(self, password_reset_service, user):
        password_reset_service.request_reset(user.email)
        success, reason = password_reset_service.confirm_reset(
            user.email, "000000", "newpass456"
        )
        assert success is False
        assert reason == "invalid"


@pytest.mark.django_db
class TestEmailVerificationService:

    def test_send_verification(self, email_verification_service, user):
        result = email_verification_service.send_verification(user.email)
        assert result is True

    def test_send_verification_nonexistent(self, email_verification_service):
        result = email_verification_service.send_verification("nobody@example.com")
        assert result is True

    def test_verify_success(self, email_verification_service, user):
        email_verification_service.send_verification(user.email)
        otp = OTPService().generate(f"email_verify:{user.pk}")

        success, reason = email_verification_service.verify(user.email, otp)
        assert success is True

        user.refresh_from_db()
        assert user.is_email_verified is True
        assert user.email_verified_at is not None

    def test_verify_wrong_otp(self, email_verification_service, user):
        email_verification_service.send_verification(user.email)
        success, reason = email_verification_service.verify(user.email, "000000")
        assert success is False
        assert reason == "invalid"
