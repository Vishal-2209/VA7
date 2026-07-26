# VA7

[![PyPI Version](https://img.shields.io/pypi/v/va7-core?label=va7-core&color=blue)](https://pypi.org/project/va7-core/)
[![PyPI Version](https://img.shields.io/pypi/v/va7-identity?label=va7-identity&color=blue)](https://pypi.org/project/va7-identity/)
[![Python Versions](https://img.shields.io/pypi/pyversions/va7-core)](https://pypi.org/project/va7-core/)
[![License](https://img.shields.io/pypi/l/va7-core)](https://github.com/Vishal-2209/VA7/blob/main/LICENSE)
[![CI](https://github.com/Vishal-2209/VA7/actions/workflows/publish.yml/badge.svg)](https://github.com/Vishal-2209/VA7/actions)
[![Downloads](https://img.shields.io/pypi/dm/va7-core?label=va7-core%20downloads)](https://pypi.org/project/va7-core/)
[![Downloads](https://img.shields.io/pypi/dm/va7-identity?label=va7-identity%20downloads)](https://pypi.org/project/va7-identity/)

A Django backend framework for SaaS applications.

## What is VA7?

VA7 is a collection of reusable Django packages that provide the infrastructure for building multi-tenant SaaS applications. Think of it as what Laravel is to PHP — a complete backend framework that extends Django with opinionated, production-ready defaults.

## Packages

| Package | Version | Purpose |
|---|---|---|
| `va7-core` | 0.1.0 | Foundation: models, events, config, middleware |
| `va7-identity` | 0.1.0 | Auth, permissions, user management |

**Status:** Feature-frozen. Building a real application to validate the design.

## Quick Start

```bash
# Install packages
pip install va7-core va7-identity
```

```python
# settings.py
INSTALLED_APPS = [
    ...
    "va7.core",
    "va7.identity",
]

MIDDLEWARE = [
    "va7.core.middleware.SecurityHeadersMiddleware",
    "va7.core.middleware.HealthCheckMiddleware",
]

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "va7.core.exceptions.custom_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

AUTHENTICATION_BACKENDS = [
    "va7.identity.backends.EmailBackend",
]
```

```python
# your_app/models.py
from va7.identity.models import AbstractRoleUser

class User(AbstractRoleUser):
    class Role(AbstractRoleUser.Role):
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"
```

## What's Inside

### va7-core
- **BaseModel** — UUID PKs, timestamps, soft-delete
- **Event Bus** — `emit()`, `listen()` for decoupling
- **Exception Handler** — Standardized DRF errors
- **Middleware** — Security headers, health check
- **Config** — Django-style lazy settings

### va7-identity
- **User Model** — AbstractRoleUser with email, role, verification
- **JWT Auth** — Login, logout, token refresh
- **Permissions** — HasRole, And, Or, Not combinators
- **Services** — Registration, password reset, email verification
- **Verification** — Pluggable VerificationMethod interface

## Documentation

- [va7-core README](packages/va7-core/README.md)
- [va7-identity README](packages/va7-identity/README.md)
- [API Stability Review](packages/va7-core/docs/STABILITY.md)
- [Authentication Guide](packages/va7-identity/docs/AUTHENTICATION.md)
- [Permissions Guide](packages/va7-identity/docs/PERMISSIONS.md)
- [Events Guide](packages/va7-identity/docs/EVENTS.md)
- [Services Guide](packages/va7-identity/docs/SERVICES.md)
- [Extension Guide](packages/va7-identity/docs/EXTENDING.md)
- [Versioning Policy](docs/VERSIONING.md)
- [Roadmap](docs/ROADMAP.md)

## Testing

```bash
# Core tests
cd packages/va7-core
pytest tests/ -v

# Identity tests
cd packages/va7-identity
pytest tests/ -v
```

## License

MIT
