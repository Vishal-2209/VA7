# Services Guide

## Overview

VA7 Identity services encapsulate business logic. Views call services; services handle the work. This separation enables reuse from non-HTTP contexts (Celery tasks, management commands, shell scripts).

## Service Architecture

```
Views (HTTP layer)
    ↓ validate input
Services (business logic)
    ↓ call models/cache
Models/Cache (data layer)
```

**Rule:** Views never touch models directly. They always go through services.

## Available Services

### RegistrationService

Handles user registration with optional email verification.

```python
from va7.identity.services import RegistrationService

service = RegistrationService()
user, require_verification = service.register(
    email="user@example.com",
    password="securepass123",
    first_name="John",
    last_name="Doe",
)
```

**Config-driven:** Verification requirement is controlled by `VA7["IDENTITY"]["REGISTRATION"]["REQUIRE_EMAIL_VERIFICATION"]`.

### PasswordResetService

Handles password reset via OTP.

```python
from va7.identity.services import PasswordResetService

service = PasswordResetService()

# Step 1: Request reset (generates OTP)
otp_sent, user = service.request_reset("user@example.com")

# Step 2: Confirm reset (validates OTP)
success, reason = service.confirm_reset("user@example.com", otp, "newpass123")
```

### EmailVerificationService

Handles email verification via OTP.

```python
from va7.identity.services import EmailVerificationService

service = EmailVerificationService()

# Step 1: Send verification (generates OTP)
otp_sent = service.send_verification("user@example.com")

# Step 2: Verify (validates OTP)
success, reason = service.verify("user@example.com", otp)
```

### OTPService

Low-level OTP generation and validation.

```python
from va7.identity.services import OTPService

service = OTPService()

# Generate
otp = service.generate("password_reset:user_id")

# Validate
is_valid, reason = service.validate("password_reset:user_id", otp)

# Rate limiting
if service.can_resend("password_reset:user_id"):
    service.increment_resend("password_reset:user_id")
```

### Token Utilities

JWT token generation and blacklisting.

```python
from va7.identity.services import generate_tokens, blacklist_refresh_token

# Generate tokens
tokens = generate_tokens(user)
# Returns: {"access": "eyJ...", "refresh": "eyJ..."}

# Blacklist a refresh token
success = blacklist_refresh_token(refresh_token)
# Returns: True if blacklisted, False if invalid/expired
```

## Using Services Outside Views

Services have no HTTP dependencies. Use them anywhere:

```python
# In a Celery task
from va7.identity.services import RegistrationService

@shared_task
def register_user_task(email, password):
    service = RegistrationService()
    user, _ = service.register(email=email, password=password)
    return str(user.pk)

# In a management command
from va7.identity.services import PasswordResetService

class Command(BaseCommand):
    def handle(self, *args, **options):
        service = PasswordResetService()
        otp_sent, user = service.request_reset("admin@example.com")
        ...
```

## Best Practices

1. **Services are stateless** — No per-request state; safe to instantiate per-call
2. **Services handle side effects** — Events are emitted from services, not views
3. **Services return tuples** — `(success, reason)` or `(result, metadata)` patterns
4. **Services don't raise** — They return success/failure tuples instead
5. **Test services independently** — No HTTP context needed
