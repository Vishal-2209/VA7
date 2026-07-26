import hashlib
import hmac
import logging
import random
import string
import time

from django.conf import settings
from django.core.cache import cache

from .base import VerificationMethod

logger = logging.getLogger("va7.identity")


class OTPMethod(VerificationMethod):
    """
    OTP verification method.

    Generates numeric OTPs, stores them in Django's cache backend,
    and validates with constant-time comparison.
    """

    name = "otp"

    def __init__(self, length=6, ttl=900, max_attempts=5):
        self.length = length
        self.ttl = ttl
        self.max_attempts = max_attempts

    def generate(self, purpose):
        """Generate an OTP. Returns the plaintext OTP string (to be sent to user)."""
        otp = "".join(random.choices(string.digits, k=self.length))
        key = self._key(purpose)
        cache.set(key, {
            "otp": self._hash(otp),
            "created_at": time.time(),
            "attempts": 0,
        }, self.ttl)
        return otp

    def validate(self, purpose, response):
        """Validate an OTP. Returns (is_valid, reason)."""
        key = self._key(purpose)
        data = cache.get(key)
        if data is None:
            return False, "expired"
        if data["attempts"] >= self.max_attempts:
            cache.delete(key)
            logger.warning("OTP max attempts reached for purpose: %s", purpose)
            return False, "max_attempts"
        if hmac.compare_digest(data["otp"], self._hash(response)):
            cache.delete(key)
            return True, "valid"
        data["attempts"] += 1
        cache.set(key, data, self.ttl)
        return False, "invalid"

    def _key(self, purpose):
        return f"va7:otp:{purpose}"

    def _hash(self, otp):
        secret = settings.SECRET_KEY
        return hmac.new(
            secret.encode(), otp.encode(), hashlib.sha256
        ).hexdigest()


class OTPService:
    """
    High-level OTP service with rate-limiting.

    Wraps OTPMethod with resend tracking.
    """

    def __init__(self, method=None, max_resends=3):
        self.method = method or OTPMethod()
        self.max_resends = max_resends

    def generate(self, purpose):
        """Generate an OTP for a given purpose."""
        return self.method.generate(purpose)

    def validate(self, purpose, otp):
        """Validate an OTP. Returns (is_valid, reason)."""
        return self.method.validate(purpose, otp)

    def can_resend(self, purpose):
        """Check if a new OTP can be sent for this purpose."""
        key = f"va7:otp:resend_count:{purpose}"
        count = cache.get(key, 0)
        return count < self.max_resends

    def increment_resend(self, purpose):
        """Increment the resend counter."""
        key = f"va7:otp:resend_count:{purpose}"
        count = cache.get(key, 0)
        cache.set(key, count + 1, self.method.ttl)
