# VA7 Identity

Authentication, authorization, and user management for Django SaaS applications.

## Installation

```bash
pip install va7-identity
```

## Quick Start

```python
# settings.py
INSTALLED_APPS = [
    ...
    "va7.core",
    "va7.identity",
]

AUTH_USER_MODEL = "your_app.User"  # Use AbstractRoleUser

AUTHENTICATION_BACKENDS = [
    "va7.identity.backends.EmailBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}
```

## User Model

```python
# your_app/models.py
from va7.identity.models import AbstractRoleUser

class User(AbstractRoleUser):
    class Role(AbstractRoleUser.Role):
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"
```

**AbstractRoleUser fields:**
- `id` — UUID primary key
- `email` — Unique, used as USERNAME_FIELD
- `username`, `first_name`, `last_name` — Optional
- `role` — Nullable CharField (for single-tenant apps)
- `is_email_verified` — Boolean
- `is_active`, `is_staff` — Standard Django fields
- `created_at`, `updated_at` — Auto-managed timestamps

**Properties:**
- `is_admin` — True if `role == "ADMIN"` or `is_superuser`
- `full_name` — Concatenation of first/last name

## Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/identity/register/` | POST | No | Create new user |
| `/identity/login/` | POST | No | Get JWT tokens |
| `/identity/logout/` | POST | Yes | Blacklist refresh token |
| `/identity/profile/` | GET/PATCH | Yes | User profile |
| `/identity/password-reset/request/` | POST | No | Request password reset OTP |
| `/identity/password-reset/confirm/` | POST | No | Confirm with OTP |
| `/identity/verify-email/` | POST | No | Verify email with OTP |
| `/identity/resend-verification/` | POST | No | Resend verification OTP |

## Project Structure

```
va7-identity/
├── pyproject.toml
├── va7/
│   ├── identity/
│   │   ├── __init__.py         # Public API (lazy imports)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── abstract_user.py # AbstractRoleUser, AbstractToken, RoleFieldMixin
│   │   ├── backends/
│   │   │   ├── __init__.py
│   │   │   └── password.py     # EmailBackend
│   │   ├── permissions/
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # HasRole
│   │   │   └── combinators.py  # And, Or, Not
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # VerificationMethod ABC
│   │   │   ├── otp.py          # OTPMethod, OTPService
│   │   │   ├── email.py        # EmailVerificationService
│   │   │   ├── registration.py # RegistrationService
│   │   │   ├── password.py     # PasswordResetService
│   │   │   └── tokens.py       # generate_tokens, blacklist_refresh_token
│   │   ├── events.py           # Event constants
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── apps.py
│   └── conf/
└── tests/
```

## Testing

```bash
pip install -e "packages/va7-identity[dev]"
pytest tests/ -v
```
