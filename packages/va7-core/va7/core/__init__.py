"""
VA7 Core — Foundation layer for Django SaaS applications.

Public API (import directly):
    from va7.core import BaseModel
    from va7.core import custom_exception_handler
    from va7.core import SecurityHeadersMiddleware, HealthCheckMiddleware
    from va7.core import emit, listen

For utilities, import from submodules:
    from va7.core.utils import get_env_variable, run_in_background
    from va7.core.mixins import ChangeTrackingMixin, SoftDeleteAdminMixin
"""

__version__ = "0.1.0"

__all__ = [
    # Models
    "BaseModel",
    # Exceptions
    "custom_exception_handler",
    # Middleware
    "SecurityHeadersMiddleware",
    "HealthCheckMiddleware",
    # Events
    "emit",
    "listen",
]


def __getattr__(name):
    """Lazy imports to avoid Django AppRegistryNotReady at module load time."""
    _lazy_imports = {
        "BaseModel": "va7.core.models",
        "custom_exception_handler": "va7.core.exceptions",
        "SecurityHeadersMiddleware": "va7.core.middleware",
        "HealthCheckMiddleware": "va7.core.middleware",
        "emit": "va7.core.events",
        "listen": "va7.core.events",
    }

    if name in _lazy_imports:
        import importlib

        module = importlib.import_module(_lazy_imports[name])
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
