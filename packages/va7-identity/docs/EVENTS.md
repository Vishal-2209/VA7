# Events Guide

## Overview

VA7 uses a synchronous event bus (from `va7-core`) for cross-package decoupling. Events are emitted during identity operations, allowing other packages to react without direct coupling.

## Available Events

| Event | Emitted When | Payload |
|---|---|---|
| `identity.user_registered` | New user created | `user` |
| `identity.user_logged_in` | Successful login | `user` |
| `identity.user_logged_out` | Logout | `user` |
| `identity.password_changed` | Password updated | `user` |
| `identity.password_reset_requested` | Reset OTP sent | `user` |
| `identity.email_verification_sent` | Verification OTP sent | `user` |
| `identity.email_verified` | Email verified | `user` |

## Listening to Events

### Decorator Pattern

```python
from va7.core.events import listen
from va7.identity.events import EVENT_USER_REGISTERED

@listen(EVENT_USER_REGISTERED)
def send_welcome_email(sender, **kwargs):
    user = kwargs["user"]
    # Send welcome email
    ...
```

### Direct Call Pattern

```python
from va7.core.events import listen

def handle_registration(sender, **kwargs):
    user = kwargs["user"]
    # Create user profile, send welcome email, etc.
    ...

listen("identity.user_registered", handle_registration)
```

## Event Listener Signature

All event listeners must accept:
- `sender` — The sender of the event (usually the class that emitted it)
- `**kwargs` — Event-specific data

```python
def my_listener(sender, **kwargs):
    user = kwargs["user"]
    ...
```

## Emitting Custom Events

You can emit your own events from application code:

```python
from va7.core.events import emit

# Emit a custom event
emit("your_app.user_activated", user=user, activated_by=admin)
```

## Event Behavior

- **Synchronous** — Listeners run in the same thread as the emit call
- **Order-dependent** — Listeners run in registration order
- **Cancellable** — If a listener returns `False`, propagation stops
- **Fault-tolerant** — Exceptions in listeners are logged but don't break other listeners

## Testing Events

```python
from va7.core.events import listen, clear

# Clear all listeners before test
def setup_function():
    clear()

def test_registration_emits_event():
    events = []
    listen("identity.user_registered", lambda sender, **kwargs: events.append(kwargs))

    # ... perform registration ...

    assert len(events) == 1
    assert events[0]["user"].email == "test@example.com"
```

## Best Practices

1. **Don't put business logic in listeners** — Listeners should be side effects (emails, notifications, logging)
2. **Keep payloads minimal** — Only include what listeners need
3. **Don't emit sensitive data** — OTPs, passwords, and tokens should NOT be in event payloads
4. **Handle failures gracefully** — Listeners should not raise exceptions
5. **Use descriptive event names** — Follow the `domain.action` pattern
