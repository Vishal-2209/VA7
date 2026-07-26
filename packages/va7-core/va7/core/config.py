import copy
import logging
import threading

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger("va7.core")

# Default configuration — every key is optional with sensible defaults
VA7_DEFAULTS = {
    "PROJECT_NAME": "VA7 Project",
    "PROJECT_SLUG": "va7-project",
    "CORE": {
        "HEALTH_CHECK_PATH": "/health/",
        "SECURITY_HEADERS": True,
    },
    "BASE_MODEL": {
        "USE_UUID": True,
        "SOFT_DELETE": True,
        "DEFAULT_ORDERING": "-created_at",
    },
    "IDENTITY": {
        "USER_MODEL": None,
        "USERNAME_FIELD": "email",
        "ROLES": {},
        "DEFAULT_ROLE": None,
        "REGISTRATION": {
            "ENABLED": True,
            "REQUIRE_EMAIL_VERIFICATION": True,
        },
        "PASSWORD_RESET": {
            "OTP_LENGTH": 6,
            "OTP_TTL": 900,
            "MAX_RESENDS": 3,
        },
        "JWT": {
            "ACCESS_LIFETIME": 15,
            "REFRESH_LIFETIME": 14,
            "CUSTOM_CLAIMS": ["role"],
            "INCLUDE_USER_IN_RESPONSE": True,
        },
    },
    "ORG": {
        "ENABLED": False,
        "MODEL": None,
        "SCOPING_FIELD": "organization_id",
    },
    "NOTIFY": {
        "ENABLED": False,
        "CHANNELS": ["IN_APP", "EMAIL"],
    },
    "BILLING": {
        "ENABLED": False,
        "PLANS": {},
        "DEFAULT_PLAN": None,
        "GATED_URLS": {},
    },
    "API": {
        "VERSION": "v1",
        "PAGE_SIZE": 20,
        "THROTTLE_RATES": {
            "anon": "100/day",
            "user": "1000/day",
        },
    },
    "STORAGE": {
        "BACKEND": "local",
    },
}


def _deep_merge(defaults: dict, overrides: dict) -> dict:
    """Deep merge overrides into defaults. Overrides take precedence."""
    result = copy.deepcopy(defaults)
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


class LazySettings:
    """
    Lazy configuration accessor for VA7 settings.

    Follows Django's LazySettings pattern:
    - Module-level instance (not singleton class)
    - Thread-safe lazy loading
    - Attribute access via __getattr__
    - Dot-notation access via get()
    - reset() for test isolation

    Usage:
        from va7.conf import settings
        roles = settings.AUTH["ROLES"]
        page_size = settings.get("API.PAGE_SIZE", 20)
    """

    _wrapped = object()

    def __init__(self):
        self.__dict__["_wrapped"] = self._wrapped
        self.__dict__["_lock"] = threading.Lock()
        self.__dict__["_loaded"] = False
        self.__dict__["_config"] = None

    def _setup(self):
        """Load configuration from Django settings, merge with defaults."""
        from django.conf import settings as django_settings

        user_config = getattr(django_settings, "VA7", {})
        self.__dict__["_config"] = _deep_merge(VA7_DEFAULTS, user_config)
        self.__dict__["_loaded"] = True
        self._validate()

    def _validate(self):
        """Validate required configuration on startup."""
        config = self.__dict__["_config"]
        if config["ORG"]["ENABLED"]:
            if not config["IDENTITY"]["ROLES"]:
                raise ImproperlyConfigured(
                    "VA7: ORG is enabled but IDENTITY.ROLES is not configured. "
                    "Set VA7['IDENTITY']['ROLES'] in your Django settings."
                )

    def _ensure_loaded(self):
        """Thread-safe lazy loading."""
        if not self.__dict__["_loaded"]:
            with self.__dict__["_lock"]:
                if not self.__dict__["_loaded"]:
                    self._setup()

    def reset(self):
        """Reset configuration state. For testing only."""
        with self.__dict__["_lock"]:
            self.__dict__["_loaded"] = False
            self.__dict__["_config"] = None

    def get(self, key_path: str, default=None):
        """Get a nested config value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., "API.PAGE_SIZE").
            default: Fallback if key not found.

        Returns:
            The config value or default.
        """
        self._ensure_loaded()

        keys = key_path.split(".")
        value = self.__dict__["_config"]
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def __getattr__(self, name):
        self._ensure_loaded()
        config = self.__dict__["_config"]
        if name not in config:
            raise AttributeError(f"VA7 config has no setting '{name}'")
        return config[name]

    def __repr__(self):
        self._ensure_loaded()
        keys = list(self.__dict__["_config"].keys())
        return f"<VA7Config [{', '.join(keys)}]>"
