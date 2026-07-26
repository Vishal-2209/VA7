"""
VA7 Identity event definitions.

Events are emitted via va7.core.events.emit() and can be listened to
via va7.core.events.listen().

Usage:
    from va7.core.events import listen
    listen("identity.user_registered", my_handler)
"""


# User lifecycle events
EVENT_USER_REGISTERED = "identity.user_registered"
EVENT_USER_LOGGED_IN = "identity.user_logged_in"
EVENT_USER_LOGGED_OUT = "identity.user_logged_out"

# Password events
EVENT_PASSWORD_CHANGED = "identity.password_changed"
EVENT_PASSWORD_RESET_REQUESTED = "identity.password_reset_requested"

# Email verification events
EVENT_EMAIL_VERIFICATION_SENT = "identity.email_verification_sent"
EVENT_EMAIL_VERIFIED = "identity.email_verified"

# All identity events (for documentation)
IDENTITY_EVENTS = [
    EVENT_USER_REGISTERED,
    EVENT_USER_LOGGED_IN,
    EVENT_USER_LOGGED_OUT,
    EVENT_PASSWORD_CHANGED,
    EVENT_PASSWORD_RESET_REQUESTED,
    EVENT_EMAIL_VERIFICATION_SENT,
    EVENT_EMAIL_VERIFIED,
]
