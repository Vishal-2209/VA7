# Extension Guide

## Overview

VA7 Identity is designed to be extended, not modified. This guide covers how to add new authentication methods, verification strategies, and custom behavior without touching framework code.

## Adding Custom Authentication Backends

VA7 Identity uses Django's native `AUTHENTICATION_BACKENDS` system. To add a new authentication method:

### 1. Create the Backend

```python
# your_app/backends/oauth_google.py
from django.contrib.auth.backends import BaseBackend

class GoogleOAuthBackend(BaseBackend):
    def authenticate(self, request, google_token=None, **kwargs):
        if not google_token:
            return None

        # Validate token with Google
        user_info = self._validate_google_token(google_token)

        # Find or create user
        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=user_info["email"],
            defaults={
                "first_name": user_info.get("given_name", ""),
                "last_name": user_info.get("family_name", ""),
            },
        )
        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _validate_google_token(self, token):
        # Call Google API, validate token, return user info
        ...
```

### 2. Register in Settings

```python
AUTHENTICATION_BACKENDS = [
    "va7.identity.backends.EmailBackend",
    "your_app.backends.oauth_google.GoogleOAuthBackend",
]
```

### 3. Add the View

```python
# your_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .backends.oauth_google import GoogleOAuthBackend

class GoogleLoginView(APIView):
    def post(self, request):
        backend = GoogleOAuthBackend()
        user = backend.authenticate(request, google_token=request.data["token"])
        if user:
            tokens = generate_tokens(user)
            return Response({"tokens": tokens})
        return Response({"error": "Invalid token"}, status=401)
```

**No framework changes needed.** The backend plugs into Django's existing system.

---

## Adding Custom Verification Methods

VA7 Identity provides a `VerificationMethod` interface for pluggable verification strategies.

### 1. Implement the Interface

```python
# your_app/verification/email_link.py
from va7.identity.services.base import VerificationMethod

class EmailLinkMethod(VerificationMethod):
    name = "email_link"

    def generate(self, purpose):
        """Generate a verification link and return it."""
        token = uuid.uuid4()
        # Store token in database with expiry
        VerificationToken.objects.create(
            purpose=purpose,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        # Return the link (to be sent via notification channel)
        return f"https://yourapp.com/verify/{token}"

    def validate(self, purpose, token):
        """Validate a verification link token."""
        try:
            vt = VerificationToken.objects.get(
                purpose=purpose,
                token=token,
                used=False,
            )
        except VerificationToken.DoesNotExist:
            return False, "invalid"

        if vt.is_expired:
            return False, "expired"

        vt.used = True
        vt.save()
        return True, "valid"
```

### 2. Use in Your Service

```python
# your_app/services.py
from va7.identity.services.email import EmailLinkMethod

class YourEmailVerificationService:
    def __init__(self):
        self.method = EmailLinkMethod()

    def send_verification(self, email):
        link = self.method.generate(f"email_verify:{user.pk}")
        # Send link via notification channel
        send_verification_email(email, link)
```

### 3. Available Verification Methods

VA7 Identity ships with:

| Method | Class | Description |
|---|---|---|
| OTP | `OTPMethod` | Numeric codes via cache |

Future methods to implement:
- Email link (see example above)
- Magic link (similar to email link, no user action needed)
- SMS verification
- Passkeys/WebAuthn

---

## Adding Custom Permissions

### 1. Create the Permission

```python
# your_app/permissions.py
from rest_framework.permissions import BasePermission

class IsWorkspaceMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.workspace.members.all()
```

### 2. Compose with VA7 Permissions

```python
from va7.identity.permissions import HasRole, And
from your_app.permissions import IsWorkspaceMember

# Must be ADMIN and a workspace member
permission_classes = [And(HasRole("ADMIN"), IsWorkspaceMember())]
```

---

## Adding Custom Events

### 1. Define Event Constants

```python
# your_app/events.py
EVENT_PROJECT_CREATED = "your_app.project_created"
EVENT_PROJECT_ARCHIVED = "your_app.project_archived"
```

### 2. Emit Events

```python
from va7.core.events import emit
from .events import EVENT_PROJECT_CREATED

def create_project(name, owner):
    project = Project.objects.create(name=name, owner=owner)
    emit(EVENT_PROJECT_CREATED, project=project, owner=owner)
    return project
```

### 3. Listen to Events

```python
from va7.core.events import listen
from your_app.events import EVENT_PROJECT_CREATED

@listen(EVENT_PROJECT_CREATED)
def notify_team(sender, **kwargs):
    project = kwargs["project"]
    # Send notification to team members
    ...
```

---

## Overriding Default Behavior

### Custom User Model

```python
# your_app/models.py
from va7.identity.models import AbstractRoleUser

class User(AbstractRoleUser):
    class Role(AbstractRoleUser.Role):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        MEMBER = "MEMBER", "Member"

    # Add custom fields
    organization = models.ForeignKey("Organization", null=True)
    avatar = models.ImageField(upload_to="avatars/", null=True)
```

### Custom Serializers

```python
# your_app/serializers.py
from va7.identity.serializers import UserSerializer

class YourUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["organization", "avatar"]
```

### Custom Views

```python
# your_app/views.py
from va7.identity.views import ProfileView

class YourProfileView(ProfileView):
    serializer_class = YourUserSerializer
```

---

## Best Practices

1. **Don't modify framework code** — Extend via inheritance and composition
2. **Use Django's native systems** — Authentication backends, middleware, etc.
3. **Keep extensions thin** — Override only what you need
4. **Test your extensions** — They're just Python classes; easy to test
5. **Document custom behavior** — Future developers need to know what you changed
