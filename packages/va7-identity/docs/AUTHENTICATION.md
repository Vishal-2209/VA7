# Authentication Guide

## Overview

VA7 Identity provides JWT-based authentication using `djangorestframework-simplejwt`. Authentication is handled by Django's native backend system — no custom wrapper.

## Setup

```python
# settings.py
AUTHENTICATION_BACKENDS = [
    "va7.identity.backends.EmailBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME_MINUTES": 15,
    "REFRESH_TOKEN_LIFETIME_DAYS": 14,
}
```

## Login Flow

1. Client sends `POST /identity/login/` with `email` and `password`
2. Server validates credentials via `EmailBackend`
3. Server returns JWT tokens:
   ```json
   {
       "user": {"id": "...", "email": "...", "role": "..."},
       "tokens": {
           "access": "eyJ...",
           "refresh": "eyJ..."
       }
   }
   ```
4. Client stores tokens and sends `Authorization: Bearer <access_token>` on subsequent requests

## Token Refresh

When the access token expires:

1. Client sends `POST /identity/token/refresh/` with `refresh` token
2. Server returns new access token

## Logout

1. Client sends `POST /identity/logout/` with `refresh` token
2. Server blacklists the refresh token
3. Client discards both tokens

## Registration Flow

1. Client sends `POST /identity/register/` with `email`, `password`, optional `first_name`, `last_name`
2. Server creates user and returns tokens
3. If email verification is required, response includes `"email_verification_required": true`
4. Client sends `POST /identity/verify-email/` with email and OTP to verify

## Password Reset Flow

1. Client sends `POST /identity/password-reset/request/` with `email`
2. Server generates OTP (delivered via notification channel)
3. Client sends `POST /identity/password-reset/confirm/` with `email`, `otp`, `new_password`
4. Password is updated

## Adding Custom Authentication Methods

VA7 Identity uses Django's native `AUTHENTICATION_BACKENDS` system. To add a new auth method:

```python
# your_app/backends.py
from django.contrib.auth.backends import BaseBackend

class OAuthGoogleBackend(BaseBackend):
    def authenticate(self, request, token=None, **kwargs):
        # Validate OAuth token, find/create user
        ...

    def get_user(self, user_id):
        # Retrieve user by ID
        ...
```

```python
# settings.py
AUTHENTICATION_BACKENDS = [
    "va7.identity.backends.EmailBackend",
    "your_app.backends.OAuthGoogleBackend",
]
```

No framework changes needed — just add the backend to the settings list.
