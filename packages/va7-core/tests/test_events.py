import threading
import time

import pytest
from django.test import TestCase

from va7.core.events import emit, listen, unlisten, clear, get_listeners


class TestEventBus(TestCase):
    """Tests for va7.core.events."""

    def setUp(self):
        clear()

    def test_listen_and_emit(self):
        results = []

        @listen("test_event")
        def handler(sender, **kwargs):
            results.append(kwargs.get("data"))

        emit("test_event", sender=None, data="hello")
        self.assertEqual(results, ["hello"])

    def test_multiple_listeners(self):
        results = []

        @listen("multi")
        def first(sender, **kwargs):
            results.append("first")

        @listen("multi")
        def second(sender, **kwargs):
            results.append("second")

        emit("multi")
        self.assertEqual(results, ["first", "second"])

    def test_emit_returns_true(self):
        @listen("ok_event")
        def handler(sender, **kwargs):
            pass

        result = emit("ok_event")
        self.assertTrue(result)

    def test_emit_returns_false_on_cancellation(self):
        @listen("cancel_event")
        def blocker(sender, **kwargs):
            return False

        @listen("cancel_event")
        def after_blocker(sender, **kwargs):
            raise AssertionError("Should not run")

        result = emit("cancel_event")
        self.assertFalse(result)

    def test_unlisten(self):
        results = []

        def handler(sender, **kwargs):
            results.append("called")

        listen("removable", handler)
        unlisten("removable", handler)
        emit("removable")
        self.assertEqual(results, [])

    def test_clear_specific_event(self):
        @listen("event_a")
        def handler_a(sender, **kwargs):
            pass

        @listen("event_b")
        def handler_b(sender, **kwargs):
            pass

        clear("event_a")
        self.assertEqual(get_listeners("event_a"), [])
        self.assertEqual(len(get_listeners("event_b")), 1)

    def test_clear_all(self):
        @listen("x")
        def h1(sender, **kwargs):
            pass

        @listen("y")
        def h2(sender, **kwargs):
            pass

        clear()
        self.assertEqual(get_listeners("x"), [])
        self.assertEqual(get_listeners("y"), [])

    def test_listener_exception_does_not_break_emit(self):
        @listen("error_event")
        def bad_handler(sender, **kwargs):
            raise ValueError("boom")

        @listen("error_event")
        def good_handler(sender, **kwargs):
            pass

        results = []

        @listen("error_event")
        def track_handler(sender, **kwargs):
            results.append("ran")

        # Should not raise
        emit("error_event")
        self.assertEqual(results, ["ran"])

    def test_get_listeners_returns_copy(self):
        @listen("copy_event")
        def handler(sender, **kwargs):
            pass

        listeners = get_listeners("copy_event")
        listeners.clear()  # Modifying the copy shouldn't affect the original
        self.assertEqual(len(get_listeners("copy_event")), 1)

    def test_listen_decorator_returns_function(self):
        @listen("decorator_test")
        def my_handler(sender, **kwargs):
            pass

        self.assertTrue(callable(my_handler))

    def test_thread_safety(self):
        results = []
        lock = threading.Lock()

        @listen("thread_event")
        def thread_handler(sender, **kwargs):
            with lock:
                results.append(1)

        threads = []
        for _ in range(10):
            t = threading.Thread(target=emit, args=("thread_event",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(results), 10)

    def test_sender_is_passed(self):
        received = []

        @listen("sender_test")
        def handler(sender, **kwargs):
            received.append(sender)

        emit("sender_test", sender="my_sender")
        self.assertEqual(received, ["my_sender"])

    def test_no_listeners_does_not_error(self):
        # Should not raise
        result = emit("nonexistent_event")
        self.assertTrue(result)
