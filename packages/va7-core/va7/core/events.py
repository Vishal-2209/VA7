"""
VA7 Event Bus — Lightweight synchronous event system for package decoupling.

Usage:
    from va7.core.events import emit, listen

    # Emit an event
    emit("user_registered", user=user, request=request)

    # Listen for an event
    def on_user_registered(sender, **kwargs):
        user = kwargs["user"]
        send_welcome_email(user)

    listen("user_registered", on_user_registered)

Design:
    - Synchronous by default (consistent with Django)
    - Events are strings (not classes) for simplicity
    - Listeners receive (sender, **kwargs)
    - emit() returns False if any listener called stop_propagation()
    - No priorities, no async, no wildcards (YAGNI for now)
"""

import logging
import threading
from collections import defaultdict

logger = logging.getLogger("va7.core.events")

# Thread-safe storage for listeners
_listeners: dict[str, list] = defaultdict(list)
_lock = threading.Lock()


def listen(event_name: str, listener=None):
    """
    Register a listener for an event.

    Can be used as a decorator:
        @listen("user_registered")
        def on_register(sender, **kwargs):
            ...

    Or called directly:
        listen("user_registered", my_handler)
    """
    if listener is not None:
        # Direct registration
        with _lock:
            _listeners[event_name].append(listener)
        return listener

    # Decorator usage
    def decorator(func):
        with _lock:
            _listeners[event_name].append(func)
        return func

    return decorator


def unlisten(event_name: str, listener):
    """Remove a listener from an event."""
    with _lock:
        if event_name in _listeners:
            try:
                _listeners[event_name].remove(listener)
            except ValueError:
                pass


def emit(event_name: str, sender=None, **kwargs):
    """
    Emit an event to all registered listeners.

    Listeners are called synchronously in registration order.
    Each listener receives (sender, **kwargs).

    Returns True if all listeners ran, False if propagation was stopped.
    """
    with _lock:
        # Copy the list to avoid issues if listeners modify it
        current_listeners = list(_listeners.get(event_name, []))

    for listener in current_listeners:
        try:
            result = listener(sender, **kwargs)
            if result is False:
                return False
        except Exception:
            logger.exception(
                "Event listener %s failed for event '%s'",
                listener.__name__ if hasattr(listener, "__name__") else str(listener),
                event_name,
            )

    return True


def clear(event_name: str = None):
    """
    Remove all listeners. Primarily for testing.

    If event_name is given, clear only that event's listeners.
    Otherwise, clear everything.
    """
    with _lock:
        if event_name:
            _listeners.pop(event_name, None)
        else:
            _listeners.clear()


def get_listeners(event_name: str) -> list:
    """Return a copy of the listeners for an event (for testing/introspection)."""
    with _lock:
        return list(_listeners.get(event_name, []))
