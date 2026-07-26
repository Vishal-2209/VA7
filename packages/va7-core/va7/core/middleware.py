import logging

from django.http import JsonResponse

logger = logging.getLogger("va7.core.middleware")


class SecurityHeadersMiddleware:
    """
    Adds security headers to all responses.

    Override CSP and other headers in your project's middleware
    by subclassing or placing your middleware after VA7's.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Content-Type-Options"] = "nosniff"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' https: wss:; "
            "frame-ancestors 'none';"
        )
        # Remove Server header if present
        if "Server" in response:
            del response["Server"]
        return response


class HealthCheckMiddleware:
    """
    Returns 200 OK for health check endpoints before ALLOWED_HOSTS validation.

    Prevents 400 errors from load balancers and deployment platforms
    (Render, Railway, Fly.io, etc.) that ping /health/ before the app is ready.

    Configure the health check path via VA7["CORE"]["HEALTH_CHECK_PATH"]
    or default to both /health/ and /api/health/.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in ("/health/", "/api/health/"):
            return JsonResponse({"status": "ok"})
        return self.get_response(request)


class TrueClientIPMiddleware:
    """
    Extracts real client IP from X-Forwarded-For / X-Real-IP headers.

    For more advanced IP detection (e.g., checking trusted proxies),
    install django-ipware and use it directly.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            request.META["REMOTE_ADDR"] = x_forwarded_for.split(",")[0].strip()
        else:
            x_real_ip = request.META.get("HTTP_X_REAL_IP")
            if x_real_ip:
                request.META["REMOTE_ADDR"] = x_real_ip
        return self.get_response(request)
