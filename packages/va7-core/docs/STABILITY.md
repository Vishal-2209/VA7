# va7-core API Stability Review

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
| `BaseModel` | `class BaseModel(models.Model)` | **Stable** | Abstract. UUID PK, `created_at`, `updated_at`, `is_deleted`. |
| `SoftDeleteManager` | `class SoftDeleteManager(models.Manager)` | **Stable** | Default manager for BaseModel. Excludes soft-deleted. |

**BaseModel fields:**
- `id` — `UUIDField(primary_key=True)`
- `created_at` — `DateTimeField(auto_now_add=True)`
- `updated_at` — `DateTimeField(auto_now=True)`
- `is_deleted` — `BooleanField(default=False)`

**BaseModel methods:**
- `soft_delete()` — Mark as deleted without removing
- `hard_delete()` — Permanently remove
- `restore()` — Undo soft delete

**BaseModel managers:**
- `objects` — Excludes soft-deleted (default)
- `all_with_deleted` — Includes soft-deleted

---

### Events

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `emit` | `emit(event_name, sender=None, **kwargs)` | **Stable** | Synchronous. Returns `False` if any listener returns `False`. |
| `listen` | `listen(event_name, listener=None)` | **Stable** | Works as decorator or direct call. |
| `unlisten` | `unlisten(event_name, listener)` | **Stable** | Removes a specific listener. |
| `clear` | `clear(event_name=None)` | **Stable** | For testing. Clears all listeners if no event specified. |
| `get_listeners` | `get_listeners(event_name)` | **Stable** | Returns a copy of the listener list. |

**Event listener signature:** `listener(sender, **kwargs)`

**Event listener return value:** If a listener returns `False`, event propagation stops and `emit()` returns `False`.

**Behavior:** Exceptions in individual listeners are logged but do not break other listeners.

---

### Exceptions

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `custom_exception_handler` | `custom_exception_handler(exc, context)` | **Stable** | Drop-in replacement for DRF's default handler. |

**Response envelope:**
```json
{
    "success": false,
    "message": "An error occurred.",
    "errors": {"field": ["error messages"]}
}
```

**Behaviors:**
- Normalizes list-shaped `detail` into `{"non_field_errors": [...]}`
- Normalizes `{"detail": "..."}` into `{"non_field_errors": ["..."]}`
- Logs all API exceptions at ERROR level
- Logs 500-series at CRITICAL level

---

### Middleware

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `SecurityHeadersMiddleware` | Standard Django middleware | **Stable** | Adds CSP, X-Content-Type-Options, etc. |
| `HealthCheckMiddleware` | Standard Django middleware | **Stable** | Responds to `/health/` and `/api/health/`. |
| `TrueClientIPMiddleware` | Standard Django middleware | **Stable** | Extracts IP from X-Forwarded-For / X-Real-IP. |

**Health check response:**
```json
{"status": "ok"}
```

---

### Mixins

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `ChangeTrackingMixin` | `class ChangeTrackingMixin(models.Model)` | **Stable** | Adds `created_by`, `updated_by` FK fields. |
| `SoftDeleteAdminMixin` | `class SoftDeleteAdminMixin(admin.ModelAdmin)` | **Stable** | Shows soft-deleted in admin, adds restore action. |

**ChangeTrackingMixin fields:**
- `created_by` — `ForeignKey(AUTH_USER_MODEL, null=True)`
- `updated_by` — `ForeignKey(AUTH_USER_MODEL, null=True)`

---

### Utilities

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `is_truthy` | `is_truthy(value: str \| None) -> bool` | **Stable** | Returns True for "true", "1", "t", "yes", "on". |
| `get_env_variable` | `get_env_variable(var_name, default=None, required_in_prod=False)` | **Stable** | Reads env vars. Raises in prod if required. |
| `run_in_background` | `run_in_background(func, *args, **kwargs)` | **Stable** | Fire-and-forget daemon thread. |
| `deprecated` | `deprecated(message)` | **Stable** | Decorator factory for deprecation warnings. |

---

### Configuration

| Symbol | Signature | Stability | Notes |
|---|---|---|---|
| `settings` | `LazySettings()` instance | **Stable** | Module-level singleton. |
| `LazySettings.get` | `settings.get(key_path, default=None)` | **Stable** | Dot-notation access. |
| `LazySettings.reset` | `settings.reset()` | **Stable** | Testing only. |

**Configuration access patterns:**
```python
from va7.conf import settings

# Attribute access (top-level keys)
roles = settings.IDENTITY["ROLES"]

# Dot notation
page_size = settings.get("API.PAGE_SIZE", 20)
```

---

## Internal APIs (Not Part of Public Surface)

These are used internally and may change without notice:

- `VA7_DEFAULTS` dict in `config.py`
- `_deep_merge()` function in `config.py`
- `IdentityUserManager` in `models/abstract_user.py`
- `TrueClientIPMiddleware` header parsing logic

---

## What's NOT in va7-core

The following are intentionally excluded from va7-core:

- User models (in va7-identity)
- Authentication backends (in va7-identity)
- Permission classes (in va7-identity)
- JWT token handling (in va7-identity)
- Organization/tenant management (future: va7-org)
- Notifications (future: va7-notify)
- Audit logging (future: va7-audit)
- Billing/subscription (future: va7-billing)
