from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Check if the user has any of the specified roles.

    Usage:
        permission_classes = [HasRole("ADMIN", "MANAGER")]
        permission_classes = [HasRole(["ADMIN", "MANAGER"])]
    """

    def __init__(self, *roles):
        if len(roles) == 1 and isinstance(roles[0], (list, tuple)):
            self.roles = set(roles[0])
        else:
            self.roles = set(roles)

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role in self.roles
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(sorted(self.roles))})"
