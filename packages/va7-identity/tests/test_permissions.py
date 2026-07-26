"""Tests for identity permissions."""

import pytest
from unittest.mock import MagicMock

from va7.identity.permissions import HasRole, And, Or, Not


def _make_request(user=None):
    request = MagicMock()
    request.user = user
    return request


def _make_authenticated_user(role="MEMBER"):
    user = MagicMock()
    user.is_authenticated = True
    user.role = role
    return user


def _make_anonymous_user():
    user = MagicMock()
    user.is_authenticated = False
    return user


class TestHasRole:

    def test_has_role_single(self):
        perm = HasRole("ADMIN")
        request = _make_request(_make_authenticated_user("ADMIN"))
        assert perm.has_permission(request, None) is True

    def test_has_role_multiple(self):
        perm = HasRole("ADMIN", "MANAGER")
        request = _make_request(_make_authenticated_user("MANAGER"))
        assert perm.has_permission(request, None) is True

    def test_has_role_list(self):
        perm = HasRole(["ADMIN", "MANAGER"])
        request = _make_request(_make_authenticated_user("ADMIN"))
        assert perm.has_permission(request, None) is True

    def test_has_role_wrong_role(self):
        perm = HasRole("ADMIN")
        request = _make_request(_make_authenticated_user("MEMBER"))
        assert perm.has_permission(request, None) is False

    def test_has_role_anonymous(self):
        perm = HasRole("ADMIN")
        request = _make_request(_make_anonymous_user())
        assert perm.has_permission(request, None) is False

    def test_has_role_no_role_attribute(self):
        perm = HasRole("ADMIN")
        user = MagicMock()
        user.is_authenticated = True
        del user.role
        request = _make_request(user)
        assert perm.has_permission(request, None) is False

    def test_repr(self):
        perm = HasRole("ADMIN", "MANAGER")
        assert "ADMIN" in repr(perm)
        assert "MANAGER" in repr(perm)


class TestAndCombinator:

    def test_all_pass(self):
        p1 = HasRole("ADMIN")
        p2 = HasRole("ADMIN")
        combinator = And(p1, p2)
        request = _make_request(_make_authenticated_user("ADMIN"))
        assert combinator.has_permission(request, None) is True

    def test_one_fails(self):
        p1 = HasRole("ADMIN")
        p2 = HasRole("MANAGER")
        combinator = And(p1, p2)
        request = _make_request(_make_authenticated_user("ADMIN"))
        assert combinator.has_permission(request, None) is False


class TestOrCombinator:

    def test_one_passes(self):
        p1 = HasRole("ADMIN")
        p2 = HasRole("MANAGER")
        combinator = Or(p1, p2)
        request = _make_request(_make_authenticated_user("ADMIN"))
        assert combinator.has_permission(request, None) is True

    def test_none_pass(self):
        p1 = HasRole("ADMIN")
        p2 = HasRole("MANAGER")
        combinator = Or(p1, p2)
        request = _make_request(_make_authenticated_user("MEMBER"))
        assert combinator.has_permission(request, None) is False


class TestNotCombinator:

    def test_invert_true(self):
        inner = HasRole("ADMIN")
        combinator = Not(inner)
        request = _make_request(_make_authenticated_user("MEMBER"))
        assert combinator.has_permission(request, None) is True

    def test_invert_false(self):
        inner = HasRole("ADMIN")
        combinator = Not(inner)
        request = _make_request(_make_authenticated_user("ADMIN"))
        assert combinator.has_permission(request, None) is False
