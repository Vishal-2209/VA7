from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from va7.core.models import BaseModel
from va7.core.mixins import ChangeTrackingMixin, SoftDeleteAdminMixin

User = get_user_model()


# --- Test models ---

class TrackedArticle(BaseModel, ChangeTrackingMixin):
    """Test model with change tracking."""
    title = models.CharField(max_length=255)

    class Meta:
        app_label = "testapp"


# --- Tests ---

class TestChangeTrackingMixin(TestCase):
    """Tests for va7.core.mixins.ChangeTrackingMixin."""

    def test_has_created_by_field(self):
        self.assertTrue(hasattr(TrackedArticle, "created_by"))

    def test_has_updated_by_field(self):
        self.assertTrue(hasattr(TrackedArticle, "updated_by"))

    def test_created_by_is_settable(self):
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass",
        )
        article = TrackedArticle(title="Test")
        article.created_by = user
        article.updated_by = user
        article.save()

        article.refresh_from_db()
        self.assertEqual(article.created_by, user)
        self.assertEqual(article.updated_by, user)

    def test_save_preserves_created_by(self):
        user1 = User.objects.create_user(
            email="user1@example.com",
            username="user1",
            password="testpass",
        )
        user2 = User.objects.create_user(
            email="user2@example.com",
            username="user2",
            password="testpass",
        )

        article = TrackedArticle(title="Test")
        article.created_by = user1
        article.updated_by = user1
        article.save()

        # Update only updated_by
        article.updated_by = user2
        article.save()

        article.refresh_from_db()
        self.assertEqual(article.created_by, user1)  # unchanged
        self.assertEqual(article.updated_by, user2)  # updated

    def test_save_without_user_fields(self):
        article = TrackedArticle(title="No User")
        article.save()

        article.refresh_from_db()
        self.assertIsNone(article.created_by)
        self.assertIsNone(article.updated_by)

    def test_fields_are_nullable(self):
        """created_by and updated_by should be nullable."""
        field = TrackedArticle._meta.get_field("created_by")
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_different_related_names(self):
        """created_by and updated_by should have distinct related names."""
        cb = TrackedArticle._meta.get_field("created_by")
        ub = TrackedArticle._meta.get_field("updated_by")
        self.assertNotEqual(cb.remote_field.related_name, ub.remote_field.related_name)


class TestSoftDeleteAdminMixin(TestCase):
    """Tests for va7.core.mixins.SoftDeleteAdminMixin."""

    def test_mixin_has_restore_action(self):
        """SoftDeleteAdminMixin should have a restore_selected action."""
        self.assertTrue(hasattr(SoftDeleteAdminMixin, "restore_selected"))

    def test_mixin_is_admin_model_admin_subclass(self):
        """SoftDeleteAdminMixin should be a subclass of admin.ModelAdmin."""
        self.assertTrue(issubclass(SoftDeleteAdminMixin, admin.ModelAdmin))
