import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class IdentityUserManager(BaseUserManager):
    """Custom manager for IdentityUser."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "ADMIN")
        return self.create_user(email, password, **extra_fields)


class AbstractRoleUser(AbstractBaseUser, PermissionsMixin):
    """
    Abstract user model with role-based access control.

    Subclass this in your app:
        class User(AbstractRoleUser):
            class Role(AbstractRoleUser.Role):
                MANAGER = "MANAGER", "Manager"
                MEMBER = "MEMBER", "Member"

    The 'role' field is nullable — for single-tenant apps, use it directly.
    For multi-tenant apps with contextual roles, ignore it and use
    membership models (from va7-org) instead.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = IdentityUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self):
        """Admin if role is ADMIN, or if is_superuser is True."""
        if self.is_superuser:
            return True
        return self.role == "ADMIN"


class AbstractToken(models.Model):
    """
    Abstract token model for password reset, email verification, etc.

    Subclass for each token type:
        class PasswordResetToken(AbstractToken):
            pass

    Does NOT inherit from BaseModel to avoid field shadowing.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_tokens",
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.__class__.__name__} for {self.user}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.used and not self.is_expired


class RoleFieldMixin(models.Model):
    """
    Mixin that adds a role field with configurable choices.

    Use this when you want roles on a non-user model:
        class Organization(BaseModel, RoleFieldMixin):
            class Role(RoleFieldMixin.Role):
                OWNER = "OWNER", "Owner"
                ADMIN = "ADMIN", "Admin"
                MEMBER = "MEMBER", "Member"
    """

    class Role(models.TextChoices):
        DEFAULT = "DEFAULT", "Default"

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.DEFAULT,
    )

    class Meta:
        abstract = True
