import json

import pytest
from django.test import TestCase, RequestFactory
from django.http import JsonResponse, HttpResponse

from va7.core.middleware import (
    SecurityHeadersMiddleware,
    HealthCheckMiddleware,
    TrueClientIPMiddleware,
)


def dummy_view(request):
    return HttpResponse("OK")


class TestSecurityHeadersMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(dummy_view)

    def test_adds_x_content_type_options(self):
        request = self.factory.get("/")
        response = self.middleware(request)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_adds_x_xss_protection(self):
        request = self.factory.get("/")
        response = self.middleware(request)
        self.assertEqual(response["X-XSS-Protection"], "1; mode=block")

    def test_adds_referrer_policy(self):
        request = self.factory.get("/")
        response = self.middleware(request)
        self.assertEqual(response["Referrer-Policy"], "strict-origin-when-cross-origin")

    def test_adds_permissions_policy(self):
        request = self.factory.get("/")
        response = self.middleware(request)
        self.assertIn("camera=()", response["Permissions-Policy"])

    def test_adds_csp(self):
        request = self.factory.get("/")
        response = self.middleware(request)
        self.assertIn("default-src 'self'", response["Content-Security-Policy"])

    def test_removes_server_header(self):
        def view_with_server(request):
            resp = HttpResponse("OK")
            resp["Server"] = "Apache/2.4"
            return resp

        middleware = SecurityHeadersMiddleware(view_with_server)
        request = self.factory.get("/")
        response = middleware(request)
        self.assertNotIn("Server", response)


class TestHealthCheckMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = HealthCheckMiddleware(dummy_view)

    def test_health_root_returns_200(self):
        request = self.factory.get("/health/")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_health_api_returns_200(self):
        request = self.factory.get("/api/health/")
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_health_returns_json(self):
        request = self.factory.get("/health/")
        response = self.middleware(request)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "ok")

    def test_non_health_path_passes_through(self):
        request = self.factory.get("/api/users/")
        response = self.middleware(request)
        # Should pass through to dummy_view, returning "OK"
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")


class TestTrueClientIPMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TrueClientIPMiddleware(dummy_view)

    def test_x_forwarded_for(self):
        request = self.factory.get("/", REMOTE_ADDR="127.0.0.1")
        request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.50, 70.41.3.18"
        response = self.middleware(request)
        self.assertEqual(request.META["REMOTE_ADDR"], "203.0.113.50")

    def test_x_real_ip(self):
        request = self.factory.get("/", REMOTE_ADDR="127.0.0.1")
        request.META["HTTP_X_REAL_IP"] = "198.51.100.1"
        response = self.middleware(request)
        self.assertEqual(request.META["REMOTE_ADDR"], "198.51.100.1")

    def test_forwarded_for_takes_precedence(self):
        request = self.factory.get("/", REMOTE_ADDR="127.0.0.1")
        request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.50"
        request.META["HTTP_X_REAL_IP"] = "198.51.100.1"
        response = self.middleware(request)
        self.assertEqual(request.META["REMOTE_ADDR"], "203.0.113.50")

    def test_no_headers_keeps_original(self):
        request = self.factory.get("/", REMOTE_ADDR="127.0.0.1")
        response = self.middleware(request)
        self.assertEqual(request.META["REMOTE_ADDR"], "127.0.0.1")
