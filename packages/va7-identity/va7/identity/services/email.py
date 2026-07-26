from django.contrib.auth import get_user_model
from django.utils import timezone

from va7.core.events import emit

from .otp import OTPService

User = get_user_model()


class EmailVerificationService:
    """
    Email verification via OTP.

    OTP is not emitted in events — it is delivered through the notification channel.
    """

    def __init__(self):
        self.otp_service = OTPService()

    def send_verification(self, email):
        """Send an email verification OTP. Returns otp_generated."""
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return True

        if not self.otp_service.can_resend(f"email_verify:{user.pk}"):
            return False

        otp = self.otp_service.generate(f"email_verify:{user.pk}")
        self.otp_service.increment_resend(f"email_verify:{user.pk}")
        emit("identity.email_verification_sent", user=user)
        return True

    def verify(self, email, otp):
        """Verify email with OTP. Returns (success, reason)."""
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return False, "invalid"

        is_valid, reason = self.otp_service.validate(
            f"email_verify:{user.pk}", otp
        )
        if not is_valid:
            return False, reason

        user.is_email_verified = True
        user.email_verified_at = timezone.now()
        user.save(update_fields=["is_email_verified", "email_verified_at"])
        emit("identity.email_verified", user=user)
        return True, "valid"
