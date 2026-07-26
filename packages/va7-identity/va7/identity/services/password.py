from django.contrib.auth import get_user_model

from va7.core.events import emit

from .otp import OTPService

User = get_user_model()


class PasswordResetService:
    """
    Password reset via OTP.

    OTP is not emitted in events — it is delivered through the notification channel.
    """

    def __init__(self):
        self.otp_service = OTPService()

    def request_reset(self, email):
        """Request a password reset. Returns (otp_generated, user_or_none)."""
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return True, None

        if not self.otp_service.can_resend(f"password_reset:{user.pk}"):
            return False, None

        otp = self.otp_service.generate(f"password_reset:{user.pk}")
        self.otp_service.increment_resend(f"password_reset:{user.pk}")
        emit("identity.password_reset_requested", user=user)
        return True, user

    def confirm_reset(self, email, otp, new_password):
        """Confirm a password reset with OTP. Returns (success, reason)."""
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return False, "invalid"

        is_valid, reason = self.otp_service.validate(
            f"password_reset:{user.pk}", otp
        )
        if not is_valid:
            return False, reason

        user.set_password(new_password)
        user.save(update_fields=["password"])
        emit("identity.password_changed", user=user)
        return True, "valid"
