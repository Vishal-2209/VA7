from unittest.mock import MagicMock

import pytest
from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    PermissionDenied,
    AuthenticationFailed,
)

from va7.core.exceptions import custom_exception_handler


class TestCustomExceptionHandler(TestCase):
    """Tests for va7.core.exceptions.custom_exception_handler."""

    def setUp(self):
        self.factory = RequestFactory()
        self.context = {"request": self.factory.get("/test/")}

    def test_returns_none_for_unhandled_exceptions(self):
        """Non-DRF exceptions should return None (let Django handle them)."""
        exc = ValueError("something unexpected")
        result = custom_exception_handler(exc, self.context)
        self.assertIsNone(result)

    def test_wraps_validation_error(self):
        exc = ValidationError({"title": ["This field is required."]})
        response = custom_exception_handler(exc, self.context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("errors", response.data)
        self.assertIn("title", response.data["errors"])

    def test_wraps_not_found(self):
        exc = NotFound()
        response = custom_exception_handler(exc, self.context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_wraps_permission_denied(self):
        exc = PermissionDenied()
        response = custom_exception_handler(exc, self.context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_wraps_authentication_failed(self):
        exc = AuthenticationFailed()
        response = custom_exception_handler(exc, self.context)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])

    def test_normalizes_list_errors(self):
        """List errors should be wrapped in non_field_errors."""
        exc = ValidationError(["Error one", "Error two"])
        response = custom_exception_handler(exc, self.context)

        self.assertIsNotNone(response)
        self.assertIn("non_field_errors", response.data["errors"])
        self.assertEqual(len(response.data["errors"]["non_field_errors"]), 2)

    def test_normalizes_detail_string(self):
        """Single 'detail' string should be wrapped in non_field_errors."""
        exc = NotFound("Object not found")
        response = custom_exception_handler(exc, self.context)

        self.assertIsNotNone(response)
        self.assertIn("non_field_errors", response.data["errors"])

    def test_response_format_has_success_field(self):
        exc = ValidationError({"field": ["error"]})
        response = custom_exception_handler(exc, self.context)

        self.assertIn("success", response.data)
        self.assertFalse(response.data["success"])
        self.assertIn("message", response.data)
        self.assertIn("errors", response.data)

    def test_view_name_in_context(self):
        """The handler should log the view name (no crash if missing)."""
        exc = ValidationError({"x": ["y"]})
        # context without 'view' key
        result = custom_exception_handler(exc, {})
        self.assertIsNotNone(result)
