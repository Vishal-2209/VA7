import logging
import os
import threading
from functools import wraps

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger("va7.core")


def is_truthy(value: str | None) -> bool:
    """Check if a string value represents a truthy boolean.

    Returns True for: 'true', '1', 't', 'yes', 'on' (case-insensitive).
    """
    return (value or "").lower() in ("true", "1", "t", "yes", "on")


def get_env_variable(var_name: str, default=None, required_in_prod: bool = False):
    """
    Get an environment variable with fallback and production validation.

    Args:
        var_name: Environment variable name.
        default: Fallback value if not set.
        required_in_prod: If True, raises ImproperlyConfigured in production.

    Returns:
        The environment variable value or default.

    Raises:
        ImproperlyConfigured: If required in production and not set.
    """
    value = os.getenv(var_name, default)

    from django.conf import settings as django_settings

    is_prod = not getattr(django_settings, "DEBUG", False)

    if is_prod and required_in_prod and (value is None or value == default):
        raise ImproperlyConfigured(
            f"VA7: Set the {var_name} environment variable in production."
        )

    return value


def run_in_background(func, *args, **kwargs):
    """
    Fire-and-forget background task using threading.

    Ensures DB connections are cleaned up after the thread completes.
    Use for lightweight tasks (emails, notifications).
    For heavy workloads, use Celery (va7-tasks).

    Returns:
        The started Thread instance.
    """

    def _target():
        try:
            func(*args, **kwargs)
        except Exception:
            logger.exception("Background task failed: %s", func.__name__)
        finally:
            from django import db

            db.connections.close_all()

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()
    return thread


def deprecated(message: str):
    """Decorator to mark functions as deprecated with a migration message."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import warnings

            warnings.warn(
                f"{func.__name__} is deprecated. {message}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
