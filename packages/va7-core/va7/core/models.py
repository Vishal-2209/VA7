import uuid

from django.db import models


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    """
    Abstract base model for all VA7 models.

    Provides:
    - UUID primary key
    - created_at / updated_at timestamps
    - Soft delete (is_deleted flag + SoftDeleteManager)

    Usage:
        class MyModel(BaseModel):
            name = models.CharField(max_length=255)

        # Default queryset excludes soft-deleted
        MyModel.objects.all()

        # Include soft-deleted
        MyModel.all_with_deleted.all()

        # Soft delete
        obj.soft_delete()

        # Restore
        obj.restore()
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    objects = SoftDeleteManager()
    all_with_deleted = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def soft_delete(self):
        """Soft delete — marks as deleted without removing the row."""
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

    def hard_delete(self):
        """Permanent delete — use with caution."""
        return super().delete()

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.save(update_fields=["is_deleted", "updated_at"])

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.pk}>"
