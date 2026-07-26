"""Tests for identity backends."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from va7.identity.backends.password import EmailBackend

User = get_user_model()


@pytest.mark.django_db
class TestEmailBackend:

    def test_authenticate_success(self, user):
        backend = EmailBackend()
        result = backend.authenticate(
            None, username="test@example.com", password="testpass123"
        )
        assert result is not None
        assert result.pk == user.pk

    def test_authenticate_wrong_password(self, user):
        backend = EmailBackend()
        result = backend.authenticate(
            None, username="test@example.com", password="wrongpass"
        )
        assert result is None

    def test_authenticate_nonexistent_user(self):
        backend = EmailBackend()
        result = backend.authenticate(
            None, username="nonexistent@example.com", password="pass123"
        )
        assert result is None

    def test_authenticate_with_email_kwarg(self, user):
        backend = EmailBackend()
        result = backend.authenticate(
            None, email="test@example.com", password="testpass123"
        )
        assert result is not None
        assert result.pk == user.pk

    def test_get_user_exists(self, user):
        backend = EmailBackend()
        result = backend.get_user(user.pk)
        assert result is not None
        assert result.pk == user.pk

    def test_get_user_nonexistent(self):
        backend = EmailBackend()
        result = backend.get_user("00000000-0000-0000-0000-000000000000")
        assert result is None

    def test_authenticate_inactive_user(self, user):
        user.is_active = False
        user.save()
        backend = EmailBackend()
        result = backend.authenticate(
            None, username="test@example.com", password="testpass123"
        )
        assert result is None

    def test_is_model_backend_subclass(self):
        assert issubclass(EmailBackend, ModelBackend)
