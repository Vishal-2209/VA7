from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    """User profile serializer."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "role", "is_email_verified", "full_name",
        ]
        read_only_fields = ["id", "email", "role", "is_email_verified"]

    def get_full_name(self, obj):
        return obj.full_name


class UserUpdateSerializer(serializers.ModelSerializer):
    """User profile update serializer."""

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "username"]


class RegisterSerializer(serializers.Serializer):
    """Registration serializer."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    username = serializers.CharField(required=False, max_length=150)


class LoginSerializer(TokenObtainPairSerializer):
    """Login serializer — extends SimpleJWT's TokenObtainPairSerializer."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        if email and password:
            attrs["username"] = email
        return super().validate(attrs)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset serializer."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirm password reset serializer."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)
    new_password = serializers.CharField(write_only=True, min_length=8)


class EmailVerificationSerializer(serializers.Serializer):
    """Email verification serializer."""

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)


class ResendVerificationSerializer(serializers.Serializer):
    """Resend email verification serializer."""

    email = serializers.EmailField()
