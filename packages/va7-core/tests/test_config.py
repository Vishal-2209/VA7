import os
import threading
import time
from unittest.mock import patch

import pytest
from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured

from va7.core.utils import is_truthy, get_env_variable, run_in_background, deprecated
from va7.core.config import LazySettings, VA7_DEFAULTS, _deep_merge


class TestIsTruthy(TestCase):
    def test_true_values(self):
        for val in ["true", "True", "TRUE", "1", "t", "yes", "on"]:
            self.assertTrue(is_truthy(val), f"Expected True for '{val}'")

    def test_false_values(self):
        for val in ["false", "False", "0", "no", "off", "something", "", None]:
            self.assertFalse(is_truthy(val), f"Expected False for '{val}'")


class TestGetEnvVariable(TestCase):
    def test_returns_value(self):
        with patch.dict(os.environ, {"VA7_TEST_VAR": "hello"}):
            result = get_env_variable("VA7_TEST_VAR")
            self.assertEqual(result, "hello")

    def test_returns_default_when_not_set(self):
        result = get_env_variable("VA7_NONEXISTENT_VAR", default="fallback")
        self.assertEqual(result, "fallback")

    @override_settings(DEBUG=True)
    def test_required_in_prod_not_enforced_in_debug(self):
        with patch.dict(os.environ, {}, clear=True):
            result = get_env_variable("VA7_MISSING", default="default", required_in_prod=True)
            self.assertEqual(result, "default")


class TestDeepMerge(TestCase):
    def test_simple_merge(self):
        defaults = {"a": 1, "b": 2}
        overrides = {"b": 3, "c": 4}
        result = _deep_merge(defaults, overrides)
        self.assertEqual(result, {"a": 1, "b": 3, "c": 4})

    def test_nested_merge(self):
        defaults = {"a": {"x": 1, "y": 2}, "b": 3}
        overrides = {"a": {"y": 99, "z": 100}}
        result = _deep_merge(defaults, overrides)
        self.assertEqual(result, {"a": {"x": 1, "y": 99, "z": 100}, "b": 3})

    def test_does_not_mutate_inputs(self):
        defaults = {"a": {"x": 1}}
        overrides = {"a": {"y": 2}}
        _deep_merge(defaults, overrides)
        self.assertEqual(defaults, {"a": {"x": 1}})
        self.assertEqual(overrides, {"a": {"y": 2}})


class TestRunInBackground(TestCase):
    def test_executes_function(self):
        results = []
        run_in_background(results.append, "done")
        time.sleep(0.1)
        self.assertEqual(results, ["done"])

    def test_returns_thread(self):
        import threading
        thread = run_in_background(lambda: None)
        self.assertIsInstance(thread, threading.Thread)


class TestDeprecated(TestCase):
    def test_warns_on_call(self):
        @deprecated("Use new_func instead.")
        def old_func():
            return 42

        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_func()
            self.assertEqual(result, 42)
            self.assertEqual(len(w), 1)
            self.assertIn("old_func", str(w[0].message))
            self.assertIn("new_func", str(w[0].message))


class TestLazySettings(TestCase):
    """Tests for the redesigned LazySettings (Django LazySettings pattern)."""

    def setUp(self):
        from va7.conf import settings
        settings.reset()

    def test_attribute_access(self):
        from va7.conf import settings
        # Test settings overrides PROJECT_NAME to "VA7 Test Project"
        self.assertEqual(settings.PROJECT_NAME, "VA7 Test Project")

    def test_get_nested_value(self):
        from va7.conf import settings
        self.assertEqual(settings.get("API.PAGE_SIZE"), 20)

    def test_get_returns_default_for_missing(self):
        from va7.conf import settings
        self.assertEqual(settings.get("NONEXISTENT.KEY", "fallback"), "fallback")

    def test_defaults_are_complete(self):
        expected_keys = {
            "PROJECT_NAME", "PROJECT_SLUG", "CORE", "BASE_MODEL",
            "IDENTITY", "ORG", "NOTIFY", "BILLING", "API", "STORAGE",
        }
        self.assertEqual(set(VA7_DEFAULTS.keys()), expected_keys)

    @override_settings(VA7={"PROJECT_NAME": "Custom"})
    def test_loads_user_config(self):
        from va7.conf import settings
        settings.reset()
        self.assertEqual(settings.PROJECT_NAME, "Custom")

    def test_missing_attribute_raises(self):
        from va7.conf import settings
        with self.assertRaises(AttributeError):
            _ = settings.NONEXISTENT

    def test_reset_clears_state(self):
        from va7.conf import settings
        settings.reset()
        # Force load
        _ = settings.PROJECT_NAME
        settings.reset()
        # Should reload on next access (still uses test settings override)
        self.assertEqual(settings.PROJECT_NAME, "VA7 Test Project")

    def test_thread_safety(self):
        """Multiple threads accessing settings should not cause race conditions."""
        from va7.conf import settings
        settings.reset()
        results = []

        def access_config():
            results.append(settings.PROJECT_NAME)

        threads = [threading.Thread(target=access_config) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 10)
        self.assertTrue(all(r == "VA7 Test Project" for r in results))

    def test_repr(self):
        from va7.conf import settings
        r = repr(settings)
        self.assertIn("VA7Config", r)
