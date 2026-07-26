from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """
    Authenticate with email + password.

    Uses Django's ModelBackend as base — just overrides the lookup.
    Add this to AUTHENTICATION_BACKENDS in your Django settings:

        AUTHENTICATION_BACKENDS = [
            "va7.identity.backends.EmailBackend",
        ]
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get("email") or username
        if email is None or password is None:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
