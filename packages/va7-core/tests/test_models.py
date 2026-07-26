import uuid

import pytest
from django.test import TestCase

from tests.testapp.models import Article, Tag


class TestBaseModel(TestCase):
    """Tests for va7.core.models.BaseModel."""

    def test_uuid_primary_key(self):
        article = Article.objects.create(title="Test")
        self.assertIsInstance(article.pk, uuid.UUID)

    def test_created_at_auto_set(self):
        article = Article.objects.create(title="Test")
        self.assertIsNotNone(article.created_at)

    def test_updated_at_auto_set(self):
        article = Article.objects.create(title="Test")
        original_updated = article.updated_at
        article.title = "Updated"
        article.save()
        article.refresh_from_db()
        self.assertGreaterEqual(article.updated_at, original_updated)

    def test_is_deleted_defaults_false(self):
        article = Article.objects.create(title="Test")
        self.assertFalse(article.is_deleted)

    def test_soft_delete(self):
        article = Article.objects.create(title="Test")
        article.soft_delete()

        # Should not appear in default queryset
        self.assertEqual(Article.objects.count(), 0)

        # Should appear in all_with_deleted queryset
        self.assertEqual(Article.all_with_deleted.count(), 1)

        # Verify is_deleted flag
        article.refresh_from_db()
        self.assertTrue(article.is_deleted)

    def test_restore(self):
        article = Article.objects.create(title="Test")
        article.soft_delete()
        self.assertEqual(Article.objects.count(), 0)

        article.restore()
        self.assertEqual(Article.objects.count(), 1)
        self.assertFalse(article.is_deleted)

    def test_hard_delete(self):
        article = Article.objects.create(title="Test")
        article.hard_delete()

        # Should not appear in any queryset
        self.assertEqual(Article.objects.count(), 0)
        self.assertEqual(Article.all_with_deleted.count(), 0)

    def test_soft_delete_updates_timestamp(self):
        article = Article.objects.create(title="Test")
        original_updated = article.updated_at
        article.soft_delete()
        article.refresh_from_db()
        self.assertGreaterEqual(article.updated_at, original_updated)
        self.assertTrue(article.is_deleted)

    def test_ordering(self):
        """Verify BaseModel has the correct default ordering in its Meta."""
        from va7.core.models import BaseModel as Base
        self.assertEqual(Base._meta.ordering, ["-created_at"])

    def test_repr(self):
        article = Article.objects.create(title="Test")
        self.assertIn("Article", repr(article))
        self.assertIn(str(article.pk), repr(article))

    def test_base_model_fields(self):
        """Verify all BaseModel fields are present on the model."""
        article = Article.objects.create(title="Fields Test")
        self.assertTrue(hasattr(article, "id"))
        self.assertTrue(hasattr(article, "created_at"))
        self.assertTrue(hasattr(article, "updated_at"))
        self.assertTrue(hasattr(article, "is_deleted"))


class TestSoftDeleteManager(TestCase):
    """Tests for SoftDeleteManager."""

    def test_objects_excludes_deleted(self):
        Article.objects.create(title="Active")
        deleted = Article.objects.create(title="Deleted")
        deleted.soft_delete()

        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(Article.objects.first().title, "Active")

    def test_all_with_deleted_includes_all(self):
        Article.objects.create(title="Active")
        deleted = Article.objects.create(title="Deleted")
        deleted.soft_delete()

        self.assertEqual(Article.all_with_deleted.count(), 2)

    def test_mix_of_active_and_deleted(self):
        Article.objects.create(title="Active 1")
        Article.objects.create(title="Active 2")
        d1 = Article.objects.create(title="Deleted 1")
        d2 = Article.objects.create(title="Deleted 2")
        d1.soft_delete()
        d2.soft_delete()

        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(Article.all_with_deleted.count(), 4)

    def test_filtering_works_on_active_queryset(self):
        Article.objects.create(title="Python")
        Article.objects.create(title="Django")
        deleted = Article.objects.create(title="Flask")
        deleted.soft_delete()

        python_articles = Article.objects.filter(title="Python")
        self.assertEqual(python_articles.count(), 1)

        flask_articles = Article.objects.filter(title="Flask")
        self.assertEqual(flask_articles.count(), 0)

    def test_restore_makes_visible_in_default_manager(self):
        article = Article.objects.create(title="Restore Me")
        article.soft_delete()
        self.assertEqual(Article.objects.count(), 0)

        article.restore()
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(Article.objects.first().title, "Restore Me")

    def test_hard_delete_removes_from_all_managers(self):
        article = Article.objects.create(title="Delete Me")
        article.hard_delete()

        self.assertEqual(Article.objects.count(), 0)
        self.assertEqual(Article.all_with_deleted.count(), 0)
