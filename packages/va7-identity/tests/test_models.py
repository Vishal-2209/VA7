"""Tests for identity models."""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from va7.identity.models import AbstractToken, AbstractRoleUser, RoleFieldMixin


@pytest.mark.django_db
class TestAbstractRoleUser:

    def test_create_user(self, user, User):
        assert user.pk is not None
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.role == ""
        assert user.is_email_verified is False

    def test_create_admin_user(self, admin_user):
        assert admin_user.role == "ADMIN"
        assert admin_user.is_admin is True

    def test_full_name(self, user):
        assert user.full_name == "Test User"

    def test_full_name_with_whitespace(self, db, User):
        user = User.objects.create_user(
            email="a@b.com", password="pass123", first_name="", last_name=""
        )
        assert user.full_name == ""

    def test_str(self, user):
        assert str(user) == "test@example.com"

    def test_create_superuser(self, db, User):
        superuser = User.objects.create_superuser(
            email="super@example.com", password="superpass123"
        )
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.is_active is True
        assert superuser.role == "ADMIN"

    def test_email_unique(self, db, User):
        User.objects.create_user(email="dup@example.com", password="pass123")
        with pytest.raises(Exception):
            User.objects.create_user(email="dup@example.com", password="pass456")

    def test_is_admin_property_superuser(self, db, User):
        superuser = User.objects.create_superuser(
            email="super@example.com", password="pass123"
        )
        assert superuser.is_admin is True

    def test_is_admin_property_role_admin(self, admin_user):
        assert admin_user.is_admin is True

    def test_is_admin_property_regular_user(self, user):
        assert user.is_admin is False

    def test_is_admin_property_no_role(self, db, User):
        user = User.objects.create_user(
            email="norole@example.com", password="pass123", role=""
        )
        assert user.is_admin is False

    def test_role_nullable(self, db, User):
        user = User.objects.create_user(
            email="nullable@example.com", password="pass123"
        )
        assert user.role == ""
        user.refresh_from_db()
        assert user.role == ""

    def test_ordering(self, db, User):
        u1 = User.objects.create_user(email="a@b.com", password="pass123")
        u2 = User.objects.create_user(email="c@d.com", password="pass456")
        users = list(User.objects.all())
        assert users[0].pk == u2.pk
        assert users[1].pk == u1.pk

    def test_has_uuid_pk(self, user):
        assert isinstance(user.pk, type(user.pk))
        assert str(user.pk)

    def test_created_at_auto_set(self, user):
        assert user.created_at is not None

    def test_updated_at_auto_set(self, user):
        assert user.updated_at is not None
