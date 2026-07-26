from django.contrib.auth import get_user_model
from django.utils import timezone

from va7.core.events import emit
from va7.conf import settings as va7_settings

User = get_user_model()


class RegistrationService:
    """
    User registration with optional email verification.
    """

    def register(self, email, password, **extra_fields):
        """Register a new user. Returns (user, email_verification_required)."""
        config = va7_settings.IDENTITY.get("REGISTRATION", {})
        require_verification = config.get("REQUIRE_EMAIL_VERIFICATION", True)

        user = User.objects.create_user(
            email=email,
            password=password,
            is_email_verified=not require_verification,
            **extra_fields,
        )

        emit("identity.user_registered", user=user, email=email)

        return user, require_verification
