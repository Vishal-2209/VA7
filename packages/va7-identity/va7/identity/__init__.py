"""
VA7 Identity — Authentication, authorization, and user management.

Public API (import directly):
    from va7.identity import AbstractRoleUser, AbstractToken
    from va7.identity import HasRole
    from va7.identity import RegistrationService, PasswordResetService
"""

__version__ = "0.1.0"

__all__ = [
    # Models
    "AbstractRoleUser",
    "AbstractToken",
    "RoleFieldMixin",
    # Backends
    "EmailBackend",
    # Permissions
    "HasRole",
    "And",
    "Or",
    "Not",
    # Services
    "OTPService",
    "OTPMethod",
    "VerificationMethod",
    "RegistrationService",
    "PasswordResetService",
    "EmailVerificationService",
    "generate_tokens",
    "blacklist_refresh_token",
    # Events
    "EVENT_USER_REGISTERED",
    "EVENT_USER_LOGGED_IN",
    "EVENT_USER_LOGGED_OUT",
    "EVENT_PASSWORD_CHANGED",
    "EVENT_PASSWORD_RESET_REQUESTED",
    "EVENT_EMAIL_VERIFICATION_SENT",
    "EVENT_EMAIL_VERIFIED",
    "IDENTITY_EVENTS",
]


def __getattr__(name):
    """Lazy imports to avoid Django AppRegistryNotReady at module load time."""
    _lazy_imports = {
        # Models
        "AbstractRoleUser": "va7.identity.models",
        "AbstractToken": "va7.identity.models",
        "RoleFieldMixin": "va7.identity.models",
        # Backends
        "EmailBackend": "va7.identity.backends",
        # Permissions
        "HasRole": "va7.identity.permissions",
        "And": "va7.identity.permissions",
        "Or": "va7.identity.permissions",
        "Not": "va7.identity.permissions",
        # Services
        "OTPService": "va7.identity.services",
        "OTPMethod": "va7.identity.services",
        "VerificationMethod": "va7.identity.services",
        "RegistrationService": "va7.identity.services",
        "PasswordResetService": "va7.identity.services",
        "EmailVerificationService": "va7.identity.services",
        "generate_tokens": "va7.identity.services",
        "blacklist_refresh_token": "va7.identity.services",
        # Events
        "EVENT_USER_REGISTERED": "va7.identity.events",
        "EVENT_USER_LOGGED_IN": "va7.identity.events",
        "EVENT_USER_LOGGED_OUT": "va7.identity.events",
        "EVENT_PASSWORD_CHANGED": "va7.identity.events",
        "EVENT_PASSWORD_RESET_REQUESTED": "va7.identity.events",
        "EVENT_EMAIL_VERIFICATION_SENT": "va7.identity.events",
        "EVENT_EMAIL_VERIFIED": "va7.identity.events",
        "IDENTITY_EVENTS": "va7.identity.events",
    }

    if name in _lazy_imports:
        import importlib
        module = importlib.import_module(_lazy_imports[name])
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
