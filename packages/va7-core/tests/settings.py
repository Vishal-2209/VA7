"""
Minimal Django settings for running VA7 core tests.
"""

import os

SECRET_KEY = "test-secret-key-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["localhost"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "va7.core",
    "tests.testapp",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = [
    "va7.core.middleware.SecurityHeadersMiddleware",
    "va7.core.middleware.HealthCheckMiddleware",
    "va7.core.middleware.TrueClientIPMiddleware",
]

ROOT_URLCONF = "tests.core_urls"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (),
    "DEFAULT_PERMISSION_CLASSES": (),
    "EXCEPTION_HANDLER": "va7.core.exceptions.custom_exception_handler",
}

USE_TZ = True
TIME_ZONE = "UTC"

VA7 = {
    "PROJECT_NAME": "VA7 Test Project",
    "PROJECT_SLUG": "va7-test",
}
