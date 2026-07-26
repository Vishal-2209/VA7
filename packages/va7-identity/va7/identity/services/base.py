from abc import ABC, abstractmethod


class VerificationMethod(ABC):
    """
    Interface for verification methods.

    Each method knows how to:
    1. Generate a verification challenge (OTP, email link, etc.)
    2. Validate a verification response

    Implement this to add new verification methods:
        class EmailLinkMethod(VerificationMethod):
            name = "email_link"
            def generate(self, purpose): ...
            def validate(self, purpose, response): ...
    """

    name: str = "base"

    @abstractmethod
    def generate(self, purpose):
        """Generate a verification challenge. Returns opaque challenge data."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, purpose, response):
        """Validate a verification response. Returns (is_valid, reason)."""
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r}>"
