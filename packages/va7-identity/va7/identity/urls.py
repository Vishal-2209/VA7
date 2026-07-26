from django.urls import path

from . import views

app_name = "va7_identity"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "password-reset/request/",
        views.RequestPasswordResetView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        views.ConfirmPasswordResetView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "verify-email/",
        views.VerifyEmailView.as_view(),
        name="verify-email",
    ),
    path(
        "resend-verification/",
        views.ResendVerificationView.as_view(),
        name="resend-verification",
    ),
]
