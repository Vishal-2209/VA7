from rest_framework.permissions import BasePermission


class And(BasePermission):
    """All permissions must pass."""

    def __init__(self, *permissions):
        self.permissions = list(permissions)

    def has_permission(self, request, view):
        return all(p.has_permission(request, view) for p in self.permissions)

    def __repr__(self):
        return f"And({', '.join(repr(p) for p in self.permissions)})"


class Or(BasePermission):
    """Any permission must pass."""

    def __init__(self, *permissions):
        self.permissions = list(permissions)

    def has_permission(self, request, view):
        return any(p.has_permission(request, view) for p in self.permissions)

    def __repr__(self):
        return f"Or({', '.join(repr(p) for p in self.permissions)})"


class Not(BasePermission):
    """Invert a permission."""

    def __init__(self, permission):
        self.permission = permission

    def has_permission(self, request, view):
        return not self.permission.has_permission(request, view)

    def __repr__(self):
        return f"Not({self.permission!r})"
