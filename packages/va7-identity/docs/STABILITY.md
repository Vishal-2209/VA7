# va7-identity API Stability Review

**Version:** 0.1.0
**Review Date:** 2026-07-26
**Status:** Feature-frozen. Only bug fixes, documentation, and performance improvements.

---

## Stability Definitions

| Level | Description |
|---|---|
| **Stable** | No breaking changes expected. Safe to use in production. |
| **Internal** | May change without notice. Use at your own risk. |
| **Experimental** | Under evaluation. May be removed or redesigned. |

---

## Public API Surface

### Models

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `AbstractRoleUser` | `class AbstractRoleUser(AbstractBaseUser, PermissionsMixin)` | **Stable** | Abstract. Email-based user with optional role. |
| `AbstractToken` | `class AbstractToken(models.Model)` | **Stable** | Abstract. For password reset / email verify tokens. |
| `RoleFieldMixin` | `class RoleFieldMixin(models.Model)` | **Stable** | Adds configurable role to any model. |

**AbstractRoleUser fields:**
- `id` — `UUIDField(primary_key=True)`
- `email` — `EmailField(unique=True)` (USERNAME_FIELD)
- `username` — `CharField(max_length=150, blank=True)`
- `first_name`, `last_name` — `CharField(max_length=150, blank=True)`
- `role` — `CharField(max_length=50, blank=True, default="")` (nullable)
- `is_active` — `BooleanField(default=True)`
- `is_staff` — `BooleanField(default=False)`
- `is_email_verified` — `BooleanField(default=False)`
- `email_verified_at` — `DateTimeField(null=True, blank=True)`
- `created_at`, `updated_at` — Auto-managed timestamps

**AbstractRoleUser properties:**
- `is_admin` — True if `is_superuser` or `role == "ADMIN"`
- `full_name` — Concatenation of first/last name

**AbstractToken fields:**
- `id` — `UUIDField(primary_key=True)`
- `user` — `ForeignKey(AUTH_USER_MODEL)`
- `token` — `UUIDField(unique=True)`
- `created_at` — `DateTimeField(auto_now_add=True)`
- `expires_at` — `DateTimeField`
- `used` — `BooleanField(default=False)`

**AbstractToken properties:**
- `is_expired` — True if current time > expires_at
- `is_valid` — True if not used and not expired

---

### Backends

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `EmailBackend` | `class EmailBackend(ModelBackend)` | **Stable** | Email + password auth. |

**EmailBackend behavior:**
- Case-insensitive email lookup
- Accepts `email` or `username` kwarg
- Checks `is_active` via `user_can_authenticate()`

**Usage:**
```python
AUTHENTICATION_BACKENDS = ["va7.identity.backends.EmailBackend"]
```

---

### Permissions

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `HasRole` | `HasRole(*roles)` | **Stable** | Check user has any of specified roles. |
| `And` | `And(*permissions)` | **Stable** | All permissions must pass. |
| `Or` | `Or(*permissions)` | **Stable** | Any permission must pass. |
| `Not` | `Not(permission)` | **Stable** | Invert a permission. |

**HasRole behavior:**
- Checks `user.is_authenticated`, `hasattr(user, "role")`, `user.role in roles`
- Accepts individual args or a list: `HasRole("ADMIN", "MANAGER")` or `HasRole(["ADMIN", "MANAGER"])`

**Usage:**
```python
from va7.identity.permissions import HasRole, And, Or

# Simple role check
permission_classes = [HasRole("ADMIN", "MANAGER")]

# Complex composition
permission_classes = [And(HasRole("ADMIN"), HasPermission("app.delete_model"))]
permission_classes = [Or(HasRole("OWNER"), HasRole("ADMIN"))]
```

---

### Services

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `VerificationMethod` | `class VerificationMethod(ABC)` | **Stable** | Interface for verification strategies. |
| `OTPMethod` | `class OTPMethod(VerificationMethod)` | **Stable** | OTP verification implementation. |
| `OTPService` | `class OTPService(method=None, max_resends=3)` | **Stable** | High-level OTP with rate-limiting. |
| `RegistrationService` | `class RegistrationService()` | **Stable** | User registration with optional email verification. |
| `PasswordResetService` | `class PasswordResetService()` | **Stable** | Password reset via OTP. |
| `EmailVerificationService` | `class EmailVerificationService()` | **Stable** | Email verification via OTP. |
| `generate_tokens` | `generate_tokens(user)` | **Stable** | Generate JWT access/refresh tokens. |
| `blacklist_refresh_token` | `blacklist_refresh_token(refresh_token)` | **Stable** | Blacklist a refresh token. Returns bool. |

**VerificationMethod interface:**
```python
class VerificationMethod(ABC):
    name: str  # e.g., "otp", "email_link", "magic_link"

    def generate(self, purpose):
        """Return challenge data (e.g., OTP string, link URL)."""

    def validate(self, purpose, response):
        """Return (is_valid: bool, reason: str)."""
```

**OTPMethod parameters:**
- `length` — OTP length (default: 6)
- `ttl` — Cache TTL in seconds (default: 900 = 15 min)
- `max_attempts` — Max validation attempts (default: 5)

**RegistrationService.register():**
```python
user, require_verification = service.register(
    email="user@example.com",
    password="securepass123",
    first_name="John",
    last_name="Doe",
)
```

**PasswordResetService.request_reset():**
```python
otp_sent, user = service.request_reset("user@example.com")
```

**PasswordResetService.confirm_reset():**
```python
success, reason = service.confirm_reset("user@example.com", otp, "newpass123")
```

**EmailVerificationService.send_verification():**
```python
otp_sent = service.send_verification("user@example.com")
```

**EmailVerificationService.verify():**
```python
success, reason = service.verify("user@example.com", otp)
```

---

### Events

| Symbol | Constant | Emitted When |
|---|---|---|
| `EVENT_USER_REGISTERED` | `"identity.user_registered"` | New user created |
| `EVENT_USER_LOGGED_IN` | `"identity.user_logged_in"` | Successful login |
| `EVENT_USER_LOGGED_OUT` | `"identity.user_logged_out"` | Logout |
| `EVENT_PASSWORD_CHANGED` | `"identity.password_changed"` | Password updated |
| `EVENT_PASSWORD_RESET_REQUESTED` | `"identity.password_reset_requested"` | Reset OTP sent |
| `EVENT_EMAIL_VERIFICATION_SENT` | `"identity.email_verification_sent"` | Verification OTP sent |
| `EVENT_EMAIL_VERIFIED` | `"identity.email_verified"` | Email verified |

**Event payloads:**
All events include `user=<User instance>`. Events do NOT include OTPs or sensitive data.

**Listening to events:**
```python
from va7.core.events import listen
from va7.identity.events import EVENT_USER_REGISTERED

@listen(EVENT_USER_REGISTERED)
def on_user_registered(sender, **kwargs):
    user = kwargs["user"]
    # Send welcome email, create profile, etc.
```

---

### Serializers

| Symbol | Stability | Notes |
|---|---|---|
| `UserSerializer` | **Stable** | ModelSerializer for user profile (read). |
| `UserUpdateSerializer` | **Stable** | ModelSerializer for profile updates. |
| `RegisterSerializer` | **Stable** | Registration input validation. |
| `LoginSerializer` | **Stable** | Extends TokenObtainPairSerializer. |
| `PasswordResetRequestSerializer` | **Stable** | Email input validation. |
| `PasswordResetConfirmSerializer` | **Stable** | OTP + new password validation. |
| `EmailVerificationSerializer` | **Stable** | Email + OTP validation. |
| `ResendVerificationSerializer` | **Stable** | Email input validation. |

---

### Views

| Symbol | URL | Method | Auth | Stability |
|---|---|---|---|---|
| `RegisterView` | `/identity/register/` | POST | No | **Stable** |
| `LoginView` | `/identity/login/` | POST | No | **Stable** |
| `LogoutView` | `/identity/logout/` | POST | Yes | **Stable** |
| `ProfileView` | `/identity/profile/` | GET/PATCH | Yes | **Stable** |
| `RequestPasswordResetView` | `/identity/password-reset/request/` | POST | No | **Stable** |
| `ConfirmPasswordResetView` | `/identity/password-reset/confirm/` | POST | No | **Stable** |
| `VerifyEmailView` | `/identity/verify-email/` | POST | No | **Stable** |
| `ResendVerificationView` | `/identity/resend-verification/` | POST | No | **Stable** |

---

### URLs

| Symbol | Stability | Notes |
|---|---|---|
| `va7_identity` namespace | **Stable** | `app_name = "va7_identity"` |

**Include in your URLconf:**
```python
from django.urls import path, include

urlpatterns = [
    path("identity/", include("va7.identity.urls")),
]
```

---

## Internal APIs (Not Part of Public Surface)

These may change without notice:

- `IdentityUserManager` — Custom user manager
- `OTPService` internals — Cache key structure, hash algorithm
- `RegistrationService` — Config access pattern
- Service instantiation pattern in views

---

## What's NOT in va7-identity

The following are intentionally excluded:

- OAuth providers (future: subclass Django's BaseBackend)
- MFA/TOTP (future: VerificationMethod implementation)
- API key authentication (future: subclass Django's BaseBackend)
- Magic link authentication (future: VerificationMethod implementation)
- Social login (future: subclass Django's BaseBackend)
- Organization-scoped roles (future: va7-org)
- Notification delivery (future: va7-notify)
