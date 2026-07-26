from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from va7.core.events import emit
from va7.identity.services.tokens import generate_tokens, blacklist_refresh_token

from .serializers import (
    EmailVerificationSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .services import (
    OTPService,
    PasswordResetService,
    RegistrationService,
    EmailVerificationService,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = RegistrationService()
        user, require_verification = service.register(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
            username=serializer.validated_data.get("username", ""),
        )

        tokens = generate_tokens(user)
        response_data = {
            "user": UserSerializer(user).data,
            "tokens": tokens,
        }
        if require_verification:
            response_data["email_verification_required"] = True

        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """Login and return JWT tokens."""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        tokens = generate_tokens(user)
        emit("identity.user_logged_in", user=user)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": tokens,
        })


class LogoutView(APIView):
    """Blacklist the refresh token to logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            blacklist_refresh_token(refresh_token)

        emit("identity.user_logged_out", user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class RequestPasswordResetView(generics.GenericAPIView):
    """Request a password reset OTP."""

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = PasswordResetService()
        otp_sent, user = service.request_reset(serializer.validated_data["email"])

        return Response({"otp_sent": otp_sent}, status=status.HTTP_200_OK)


class ConfirmPasswordResetView(generics.GenericAPIView):
    """Confirm password reset with OTP."""

    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = PasswordResetService()
        success, reason = service.confirm_reset(
            email=serializer.validated_data["email"],
            otp=serializer.validated_data["otp"],
            new_password=serializer.validated_data["new_password"],
        )

        if success:
            return Response({"success": True})
        return Response(
            {"success": False, "error": reason},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyEmailView(generics.GenericAPIView):
    """Verify email with OTP."""

    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = EmailVerificationService()
        success, reason = service.verify(
            email=serializer.validated_data["email"],
            otp=serializer.validated_data["otp"],
        )

        if success:
            return Response({"success": True})
        return Response(
            {"success": False, "error": reason},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResendVerificationView(generics.GenericAPIView):
    """Resend email verification OTP."""

    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = EmailVerificationService()
        otp_sent = service.send_verification(serializer.validated_data["email"])

        return Response({"otp_sent": otp_sent}, status=status.HTTP_200_OK)
