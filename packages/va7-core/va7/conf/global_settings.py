"""
VA7 global default settings.

These are the production-ready defaults that ship with VA7.
Override any of these in your Django settings.py via the VA7 dict.

Example:
    # settings.py
    VA7 = {
        "PROJECT_NAME": "My App",
        "IDENTITY": {
            "ROLES": {
                "ADMIN": {"label": "Admin", "is_admin": True},
                "MEMBER": {"label": "Member", "is_admin": False},
            },
        },
    }
"""

# These mirror VA7_DEFAULTS in config.py but are exposed here
# for documentation and IDE autocomplete purposes.

PROJECT_NAME = "VA7 Project"
PROJECT_SLUG = "va7-project"

# Core
CORE_HEALTH_CHECK_PATH = "/health/"
CORE_SECURITY_HEADERS = True

# Base model
BASE_MODEL_USE_UUID = True
BASE_MODEL_SOFT_DELETE = True
BASE_MODEL_DEFAULT_ORDERING = "-created_at"

# Identity
IDENTITY_USER_MODEL = None
IDENTITY_USERNAME_FIELD = "email"
IDENTITY_ROLES = {}
IDENTITY_DEFAULT_ROLE = None
IDENTITY_REGISTRATION_ENABLED = True
IDENTITY_REQUIRE_EMAIL_VERIFICATION = True
IDENTITY_OTP_LENGTH = 6
IDENTITY_OTP_TTL = 900  # 15 minutes
IDENTITY_OTP_MAX_RESENDS = 3
IDENTITY_JWT_ACCESS_LIFETIME = 15  # minutes
IDENTITY_JWT_REFRESH_LIFETIME = 14  # days
IDENTITY_JWT_CUSTOM_CLAIMS = ["role"]
IDENTITY_JWT_INCLUDE_USER_IN_RESPONSE = True

# Organizations
ORG_ENABLED = False
ORG_MODEL = None
ORG_SCOPING_FIELD = "organization_id"

# Notifications
NOTIFY_ENABLED = False
NOTIFY_CHANNELS = ["IN_APP", "EMAIL"]

# Billing
BILLING_ENABLED = False
BILLING_PLANS = {}
BILLING_DEFAULT_PLAN = None
BILLING_GATED_URLS = {}

# API
API_VERSION = "v1"
API_PAGE_SIZE = 20
API_THROTTLE_ANON = "100/day"
API_THROTTLE_USER = "1000/day"

# Storage
STORAGE_BACKEND = "local"
