from django.urls import path

from apps.accounts.api.views import (
    GDPRDeleteRequestView,
    LoginView,
    MeView,
    RefreshTokenView,
    RegisterView,
    TOTPConfirmView,
    TOTPSetupView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("2fa/setup/", TOTPSetupView.as_view(), name="auth-2fa-setup"),
    path("2fa/confirm/", TOTPConfirmView.as_view(), name="auth-2fa-confirm"),
    path("gdpr/delete-request/", GDPRDeleteRequestView.as_view(), name="gdpr-delete"),
]
