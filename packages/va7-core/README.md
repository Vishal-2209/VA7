# VA7 Core

Foundation layer for Django SaaS applications.

## Installation

```bash
pip install va7-core
```

## Quick Start

```python
# settings.py
INSTALLED_APPS = [
    ...
    "va7.core",
]

MIDDLEWARE = [
    "va7.core.middleware.SecurityHeadersMiddleware",
    "va7.core.middleware.HealthCheckMiddleware",
    # "va7.core.middleware.TrueClientIPMiddleware",  # Optional
]

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "va7.core.exceptions.custom_exception_handler",
}
```

## What's Included

- **BaseModel** — UUID PKs, timestamps, soft-delete
- **Event Bus** — `emit()`, `listen()` for cross-package decoupling
- **Exception Handler** — Standardized DRF error responses
- **Middleware** — Security headers, health check, client IP
- **Config** — Django-style lazy settings with deep merge
- **Mixins** — Change tracking, soft-delete admin

## Project Structure

```
va7-core/
├── pyproject.toml
├── va7/
│   ├── core/
│   │   ├── __init__.py       # Public API (lazy imports)
│   │   ├── models.py         # BaseModel, SoftDeleteManager
│   │   ├── events.py         # Event bus (emit, listen, unlisten)
│   │   ├── exceptions.py     # custom_exception_handler
│   │   ├── middleware.py      # SecurityHeaders, HealthCheck, ClientIP
│   │   ├── mixins.py         # ChangeTrackingMixin, SoftDeleteAdminMixin
│   │   ├── utils.py          # is_truthy, get_env_variable, run_in_background
│   │   └── config.py         # LazySettings, VA7_DEFAULTS
│   └── conf/
│       ├── __init__.py       # settings = LazySettings()
│       └── global_settings.py # Documented defaults
└── tests/
    ├── test_config.py
    ├── test_events.py
    ├── test_exceptions.py
    ├── test_middleware.py
    ├── test_mixins.py
    └── test_models.py
```

## Configuration

All configuration is optional with sensible defaults. Override in `settings.py`:

```python
VA7 = {
    "PROJECT_NAME": "My SaaS",
    "IDENTITY": {
        "ROLES": {
            "ADMIN": {"label": "Admin", "is_admin": True},
            "MEMBER": {"label": "Member", "is_admin": False},
        },
    },
}
```

Access configuration:

```python
from va7.conf import settings

# Attribute access
page_size = settings.API["PAGE_SIZE"]

# Dot notation
page_size = settings.get("API.PAGE_SIZE", 20)
```

## Testing

```bash
pip install -e "packages/va7-core[dev]"
pytest tests/ -v
```
