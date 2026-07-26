# Permissions Guide

## Overview

VA7 Identity provides DRF permission classes for role-based access control. The system is designed to replace repetitive permission classes with composable building blocks.

## HasRole

The primary permission class. Checks if the authenticated user has one of the specified roles.

```python
from va7.identity.permissions import HasRole

# Single role
permission_classes = [HasRole("ADMIN")]

# Multiple roles (any match)
permission_classes = [HasRole("ADMIN", "MANAGER")]

# List form
permission_classes = [HasRole(["ADMIN", "MANAGER", "OWNER"])]
```

### Behavior

- Returns `True` if user is authenticated AND `user.role` is in the specified roles
- Returns `False` for anonymous users
- Returns `False` if user model has no `role` attribute (safe fallback)

## Permission Combinators

### And

All permissions must pass.

```python
from va7.identity.permissions import HasRole, And

# User must be ADMIN AND have a specific Django permission
permission_classes = [And(HasRole("ADMIN"), HasPermission("app.delete_model"))]
```

### Or

Any permission must pass.

```python
from va7.identity.permissions import HasRole, Or

# User can be OWNER or ADMIN
permission_classes = [Or(HasRole("OWNER"), HasRole("ADMIN"))]
```

### Not

Invert a permission.

```python
from va7.identity.permissions import HasRole, Not

# User must NOT be a GUEST
permission_classes = [Not(HasRole("GUEST"))]
```

## Combining Permissions

Combinators can be nested for complex logic:

```python
# Must be (ADMIN or MANAGER) AND have specific permission
permission_classes = [
    And(
        Or(HasRole("ADMIN"), HasRole("MANAGER")),
        HasPermission("app.change_model"),
    )
]
```

## Django's Built-in Permissions

VA7 Identity also supports DRF's built-in permission classes:

```python
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

# Django model permissions
permission_classes = [DjangoModelPermissions]

# Simple authentication check
permission_classes = [IsAuthenticated]
```

## Best Practices

1. **Keep permissions simple** — Use `HasRole` for most cases
2. **Compose when needed** — Use `And`/`Or`/`Not` for complex rules
3. **Default to restrictive** — Start with `IsAuthenticated` and add role checks
4. **Document permission requirements** — View docstrings should list required roles
5. **Test permission classes** — They're just functions; easy to unit test
