"""
JWT token service.

Generates token pairs and builds auth responses.
Business logic for JWT lives here, not in views.
"""

from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens(user):
    """Generate a JWT token pair for a user. Returns dict with access/refresh."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def blacklist_refresh_token(refresh_token):
    """
    Blacklist a refresh token.

    Returns True if blacklisted, False if token was invalid/expired.
    Logs errors but does not raise.
    """
    import logging
    logger = logging.getLogger("va7.identity")
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return True
    except Exception as e:
        logger.warning("Failed to blacklist refresh token: %s", e)
        return False
