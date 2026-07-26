"""
VA7 Model Mixins — Optional reusable model behaviors.

These mixins complement BaseModel by adding optional fields and admin support.
Projects opt-in by using the mixin, not by configuring BaseModel.
"""

from django.conf import settings
from django.contrib import admin
from django.db import models


class ChangeTrackingMixin(models.Model):
    """
    Optional mixin to track who created and last modified a record.

    Usage:
        class Article(BaseModel, ChangeTrackingMixin):
            title = models.CharField(max_length=255)

            def save(self, *args, **kwargs):
                user = kwargs.pop("user", None)
                if user:
                    if not self.pk:
                        self.created_by = user
                    self.updated_by = user
                super().save(*args, **kwargs)

    Or set fields directly:
        article.created_by = user
        article.updated_by = user
        article.save()

    This mixin provides the fields only. Population is the project's responsibility.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True


class SoftDeleteAdminMixin(admin.ModelAdmin):
    """
    Admin mixin that shows soft-deleted objects and provides restore actions.

    Usage:
        @admin.register(Article)
        class ArticleAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
            list_display = ["title", "is_deleted"]

    Features:
        - Shows is_deleted in list display
        - Filter by deletion status
        - Restore action for soft-deleted objects
    """

    def get_queryset(self, request):
        """Use all_with_deleted to show soft-deleted objects in admin."""
        qs = super().get_queryset(request)
        if hasattr(qs, "all_with_deleted"):
            return qs.all_with_deleted.all()
        return qs

    def get_list_filter(self, request):
        """Add is_deleted to list filters if not already present."""
        filters = list(super().get_list_filter(request))
        if "is_deleted" not in filters:
            filters.append("is_deleted")
        return filters

    @admin.action(description="Restore selected items")
    def restore_selected(self, request, queryset):
        """Restore soft-deleted objects."""
        count = 0
        for obj in queryset.filter(is_deleted=True):
            obj.restore()
            count += 1
        self.message_user(request, f"Restored {count} item(s).")

    def get_actions(self, request):
        """Add restore action for admin."""
        actions = super().get_actions(request)
        if "restore_selected" not in actions:
            actions["restore_selected"] = (
                self.restore_selected,
                "restore_selected",
                "Restore selected items",
            )
        return actions
